"""Fetch the model's input series from source and store them as a dated vintage.

Every run writes to data/vintages/<YYYY-MM-DD>/ and never overwrites an existing
vintage. That matters: real-time data cannot be reconstructed after the fact, so
capturing it at ingest is the only chance. With vintages on disk the backtest can
later run against the data actually available at each origin, rather than against
today's revised history.

    python ingest.py            fetch today's vintage
    python ingest.py --panel    also rebuild uk_quarterly.csv from it
    python ingest.py --list     show stored vintages
"""
import json, os, sys, csv, datetime as dt, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
VDIR = os.path.join(ROOT, 'data', 'vintages')
UA   = {'User-Agent': 'uk-macro-model/1.0 (+https://github.com/ddmsolutions/macroeconomic-model)'}

ONS = {   # name: (series id, dataset, topic path)
    'cpi'   : ('d7g7', 'mm23', 'economy/inflationandpriceindices'),
    'p'     : ('d7bt', 'mm23', 'economy/inflationandpriceindices'),
    'food'  : ('d7g8', 'mm23', 'economy/inflationandpriceindices'),
    'serv'  : ('d7nn', 'mm23', 'economy/inflationandpriceindices'),
    'g'     : ('ihyq', 'pn2',  'economy/grossdomesticproductgdp'),
    'u'     : ('mgsx', 'lms',  'employmentandlabourmarket/peoplenotinwork/unemployment'),
    'pay'   : ('kai9', 'lms',  'employmentandlabourmarket/peopleinwork/earningsandworkinghours'),
    'inact' : ('lf2s', 'lms',  'employmentandlabourmarket/peoplenotinwork/economicinactivity'),
}
BOE  = {'i': 'IUQABEDR', 'eri': 'XUQLBK67', 'usdgbp': 'XUQLUSS'}
FRED = {'oil': 'DCOILBRENTEU'}

def _get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')

MQ = {'MAR': 1, 'JUN': 2, 'SEP': 3, 'DEC': 4}

def fetch_ons(sid, dataset, topic):
    """Quarterly where published; otherwise the quarter-end month, as series.py does."""
    raw = _get('https://www.ons.gov.uk/%s/timeseries/%s/%s/data' % (topic, sid, dataset))
    d = json.loads(raw); out = []
    for o in d.get('quarters', []):
        try: out.append((o['date'].replace(' ', ''), float(o['value']), o.get('updateDate', '')))
        except (ValueError, KeyError): pass
    if out: return out, raw
    for o in d.get('months', []):                      # monthly-only series, e.g. AWE
        try:
            y, mon = o['date'].split()
            if mon.upper()[:3] in MQ:
                out.append(('%sQ%d' % (y, MQ[mon.upper()[:3]]), float(o['value']), o.get('updateDate', '')))
        except (ValueError, KeyError): pass
    return out, raw

def fetch_boe(code):
    url = ('https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes'
           '&Datefrom=01/Jan/1970&Dateto=31/Dec/2030&SeriesCodes=%s&CSVF=TN&UsingCodes=Y&VPD=Y&VFD=N' % code)
    raw = _get(url); out = []
    for line in raw.strip().splitlines()[1:]:
        parts = line.split(',')
        if len(parts) < 2: continue
        try:
            d = dt.datetime.strptime(parts[0].strip(), '%d %b %Y')
            out.append(('%dQ%d' % (d.year, (d.month - 1) // 3 + 1), float(parts[1]), ''))
        except ValueError: pass
    return out, raw

def fetch_fred(sid):
    raw = _get('https://fred.stlouisfed.org/graph/fredgraph.csv?id=%s' % sid)
    b = {}
    for line in raw.strip().splitlines()[1:]:
        parts = line.split(',')
        if len(parts) < 2 or parts[1] in ('.', ''): continue
        try:
            d = dt.datetime.strptime(parts[0], '%Y-%m-%d')
            b.setdefault('%dQ%d' % (d.year, (d.month - 1) // 3 + 1), []).append(float(parts[1]))
        except ValueError: pass
    return [(q, sum(v) / len(v), '') for q, v in sorted(b.items())], raw

def run(rebuild_panel=False, stamp=None):
    stamp = stamp or dt.date.today().isoformat()
    vdir = os.path.join(VDIR, stamp)
    if os.path.exists(vdir):
        print('vintage %s exists, not overwriting. Delete it to refetch.' % stamp); return vdir
    os.makedirs(os.path.join(vdir, 'raw'), exist_ok=True)
    manifest, ok, bad = {}, 0, 0
    jobs = ([(n, 'ons', a) for n, a in ONS.items()] +
            [(n, 'boe', (c,)) for n, c in BOE.items()] +
            [(n, 'fred', (c,)) for n, c in FRED.items()])
    for name, src, args in jobs:
        try:
            rows, raw = {'ons': fetch_ons, 'boe': fetch_boe, 'fred': fetch_fred}[src](*args)
            if not rows: raise ValueError('no observations parsed')
            with open(os.path.join(vdir, name + '.csv'), 'w', newline='') as f:
                w = csv.writer(f); w.writerow(['period', 'value', 'updated']); w.writerows(rows)
            with open(os.path.join(vdir, 'raw', '%s.%s' % (name, 'json' if src == 'ons' else 'csv')), 'w', encoding='utf-8') as f:
                f.write(raw)
            manifest[name] = {'source': src, 'locator': list(args), 'n': len(rows),
                              'first': rows[0][0], 'last': rows[-1][0], 'last_value': rows[-1][1]}
            print('  ok   %-7s %-5s n=%-4d %s .. %s  last=%s' % (name, src, len(rows), rows[0][0], rows[-1][0], rows[-1][1]))
            ok += 1
        except Exception as e:
            manifest[name] = {'source': src, 'locator': list(args), 'error': str(e)[:200]}
            print('  FAIL %-7s %-5s %s' % (name, src, str(e)[:70])); bad += 1
    manifest['_meta'] = {'fetched': dt.datetime.now().isoformat(timespec='seconds'), 'ok': ok, 'failed': bad}
    with open(os.path.join(vdir, 'manifest.json'), 'w') as f: json.dump(manifest, f, indent=1)
    print('\nvintage %s: %d ok, %d failed -> %s' % (stamp, ok, bad, vdir))
    if rebuild_panel: build_panel(vdir)
    return vdir

def build_panel(vdir):
    import pandas as pd
    cols = ['g', 'cpi', 'u', 'i', 'oil', 'usdgbp', 'p']
    data = {}
    for c in cols:
        fp = os.path.join(vdir, c + '.csv')
        if not os.path.exists(fp): print('  missing %s, panel not rebuilt' % c); return None
        s = pd.read_csv(fp, index_col=0)['value']
        s.index = pd.PeriodIndex(s.index, freq='Q'); data[c] = s
    df = pd.DataFrame(data).dropna(how='all')
    out = os.path.join(vdir, 'uk_quarterly.csv'); df.to_csv(out)
    print('  panel: %d quarters, %s .. %s -> %s' % (len(df), df.index[0], df.index[-1], out))
    print('  NOTE: household energy (he) is not sourced here; carry it from the existing panel.')
    return out

def list_vintages():
    if not os.path.isdir(VDIR): print('no vintages yet'); return
    for v in sorted(os.listdir(VDIR)):
        mf = os.path.join(VDIR, v, 'manifest.json')
        if os.path.exists(mf):
            m = json.load(open(mf)).get('_meta', {})
            print('  %s  %s ok, %s failed  (%s)' % (v, m.get('ok'), m.get('failed'), m.get('fetched')))

if __name__ == '__main__':
    if '--list' in sys.argv: list_vintages()
    else: run(rebuild_panel='--panel' in sys.argv)
