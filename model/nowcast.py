"""Nowcast the current quarter from monthly indicators.

fc.py previously carried a hand-computed number and its reasoning in a comment:

    # nowcast: 2026Q3 GDP growth 0.5% (July monthly GDP carry-over 0.6%,
    # September flash PMI 51.7 implies about 0.3%; weights 2/3, 1/3)
    NOWCAST = 0.5

That is the right calculation, done by hand and re-typed each quarter. This does
it in code, so the jumping-off point is reproducible and the backtest can see the
same number the published forecast uses.

Method, deliberately simple arithmetic rather than estimation:

GDP   the monthly GVA index averaged over the quarter, against the previous
      quarter's average. Months not yet published are held at the last published
      level, which is the standard carry-over convention and the one the comment
      above used.

CPI   the quarterly annual rate is the mean of the three monthly annual rates, so
      published months are averaged directly and any missing month is held at the
      latest reading.

PMI is deliberately not included: it is proprietary and cannot be fetched, so the
hand-blend of carry-over and PMI is not reproducible here. Where PMI is available
it can be blended in through the `pmi` argument.

    python nowcast.py
"""
import json, sys, urllib.request, datetime as dt

UA = {'User-Agent': 'uk-macro-model/1.0 (+https://github.com/ddmsolutions/macroeconomic-model)'}
MON = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']

def _ons_monthly(sid, dataset, topic):
    url = 'https://www.ons.gov.uk/%s/timeseries/%s/%s/data' % (topic, sid, dataset)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        d = json.loads(r.read().decode('utf-8', 'replace'))
    out = {}
    for o in d.get('months', []):
        try:
            y, m = o['date'].split()
            out[(int(y), MON.index(m.upper()[:3]) + 1)] = float(o['value'])
        except (ValueError, KeyError): pass
    return out

def _q(ym): return (ym[0], (ym[1] - 1) // 3 + 1)
def _months_of(y, q): return [(y, m) for m in range((q - 1) * 3 + 1, (q - 1) * 3 + 4)]
def _prev_q(y, q): return (y - 1, 4) if q == 1 else (y, q - 1)

def gdp_nowcast(series=None):
    """Carry-over estimate of q/q GDP growth for the latest incomplete quarter."""
    s = series or _ons_monthly('ecy2', 'mgdp', 'economy/grossdomesticproductgdp')
    last = max(s); y, q = _q(last)
    cur, prev = _months_of(y, q), _months_of(*_prev_q(y, q))
    if not all(m in s for m in prev): return None
    have = [m for m in cur if m in s]
    if not have: return None
    carried = [s[m] if m in s else s[have[-1]] for m in cur]   # hold missing months flat
    g = (sum(carried) / 3) / (sum(s[m] for m in prev) / 3) * 100 - 100
    return {'quarter': '%dQ%d' % (y, q), 'growth': g, 'months_published': len(have),
            'latest_month': '%d-%02d' % have[-1], 'carried_forward': 3 - len(have),
            'monthly_index': [round(s[m], 2) if m in s else None for m in cur]}

def cpi_nowcast(series=None):
    """Quarterly CPI annual rate from published months of the current quarter."""
    s = series or _ons_monthly('d7g7', 'mm23', 'economy/inflationandpriceindices')
    last = max(s); y, q = _q(last)
    cur = _months_of(y, q); have = [m for m in cur if m in s]
    if not have: return None
    vals = [s[m] for m in have]
    return {'quarter': '%dQ%d' % (y, q), 'rate': sum(vals) / len(vals) * 1.0 if len(vals) == 3
            else (sum(vals) + s[have[-1]] * (3 - len(vals))) / 3,
            'months_published': len(have), 'monthly_rates': vals,
            'latest_month': '%d-%02d' % have[-1]}

def nowcast(pmi_growth=None, pmi_weight=1/3.):
    g, c = gdp_nowcast(), cpi_nowcast()
    if g and pmi_growth is not None:
        g['carry_over_only'] = g['growth']
        g['growth'] = (1 - pmi_weight) * g['growth'] + pmi_weight * pmi_growth
        g['pmi_growth'], g['pmi_weight'] = pmi_growth, pmi_weight
    return {'gdp': g, 'cpi': c, 'asof': dt.date.today().isoformat()}

if __name__ == '__main__':
    n = nowcast()
    g, c = n['gdp'], n['cpi']
    print('Nowcast as at %s\n' % n['asof'])
    if g:
        print('GDP  %s  q/q %+.2f%%' % (g['quarter'], g['growth']))
        print('     monthly GVA index %s' % g['monthly_index'])
        print('     %d of 3 months published (latest %s), %d carried forward flat'
              % (g['months_published'], g['latest_month'], g['carried_forward']))
    if c:
        print('\nCPI  %s  annual rate %.2f%%' % (c['quarter'], c['rate']))
        print('     monthly rates %s, %d of 3 published (latest %s)'
              % (c['monthly_rates'], c['months_published'], c['latest_month']))
    print('\nSet these in fc.py as NOWCAST and the CPI bisection target.')
