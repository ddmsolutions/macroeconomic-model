"""Inject the generated exports into index.html.

The dashboard embeds its data as literals rather than fetching them, so there was no
way to refresh the page after re-running the model except by hand. This does it.

It DEEP MERGES rather than replaces, and that matters at more than one level.
index.html's RQ object carries four top-level keys (bt, cpih_gap, ihist, w0) that no
script in this repo produces; they were added to the HTML directly. RQ.hist likewise
carries a `cpi` array the export does not write, and the page reads it at runtime.

A straight overwrite deletes both sets silently. A shallow merge saves the first and
still loses the second. So the merge recurses: export values win at the leaves, and any
key the exports do not generate survives at whatever depth it sits.

An object is skipped entirely if the export rewrites some parallel arrays but leaves an
orphan array beside them at a different length. The page then iterates the new length and
indexes past the end of the stale one, which breaks at runtime even though the JSON parses.
Unrelated arrays of different lengths in the same object are fine and are not flagged.

    python build_html.py            write index.html, keeping a .bak
    python build_html.py --dry-run  report what would change and touch nothing
"""
import json, os, re, shutil, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
MAP  = {'M': 'model_export.json', 'RQ': 'rpi_export.json', 'E2': 'est2_export.json'}

def deep_merge(cur, new):
    """new wins at the leaves; keys only in cur survive at any depth."""
    if not isinstance(cur, dict) or not isinstance(new, dict): return new
    out = dict(cur)
    for k, v in new.items():
        out[k] = deep_merge(cur[k], v) if k in cur else v
    return out

def orphans(cur, new, path=''):
    """Every key present in cur but not in new, at any depth, as dotted paths."""
    out = []
    if not isinstance(cur, dict) or not isinstance(new, dict): return out
    for k in cur:
        p = '%s.%s' % (path, k) if path else k
        if k not in new: out.append(p)
        else: out.extend(orphans(cur[k], new[k], p))
    return sorted(out)

def coupling_risk(cur, new, path=''):
    """Orphan arrays left at a stale length beside arrays the export rewrote.

    The real hazard is narrow: within one object the export regenerates some parallel
    arrays and not an orphan sitting alongside them, so the page iterates the new length
    and indexes past the end of the old one. That is the RQ.hist case, where q, rpi, mip
    and rpix came back at 12 while hist.cpi stayed at 6.

    Two unrelated arrays of different length in the same object are not a problem and must
    not be flagged, or the check blocks harmless writes (ihist at 36 beside a three-element
    range, for instance). So this only fires when an orphan array's length differs from the
    lengths of the arrays that WERE rewritten in the same object.
    """
    bad = []
    if not isinstance(cur, dict) or not isinstance(new, dict): return bad
    rewritten = {k: len(v) for k, v in new.items() if isinstance(v, list) and k in cur}
    orphans_  = {k: len(v) for k, v in cur.items() if isinstance(v, list) and k not in new}
    if rewritten and orphans_:
        sizes = set(rewritten.values())
        for k, n in orphans_.items():
            if n not in sizes:
                bad.append('%s: %s stays at %d while %s rewritten to %s'
                           % (path or '<root>', k, n, ', '.join(sorted(rewritten)), '/'.join(str(x) for x in sorted(sizes))))
    for k in set(cur) & set(new):
        bad.extend(coupling_risk(cur[k], new[k], '%s.%s' % (path, k) if path else k))
    return bad

def find_object(text, name):
    """Locate `const <name>={...}` and return (json_text, start, end) by brace matching."""
    anchor = 'const %s=' % name
    i = text.find(anchor)
    if i < 0: return None
    start = i + len(anchor)
    if text[start] != '{': return None
    depth = 0
    for j in range(start, len(text)):
        c = text[j]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return text[start:j + 1], start, j + 1
    return None

def main(dry=False):
    here = os.path.dirname(os.path.abspath(__file__))
    text = open(HTML, encoding='utf-8').read()
    original = text
    report = []
    for name, fn in MAP.items():
        path = os.path.join(here, fn)
        if not os.path.exists(path):
            report.append((name, 'SKIP', '%s not found' % fn)); continue
        found = find_object(text, name)
        if not found:
            report.append((name, 'SKIP', 'const %s= not found in index.html' % name)); continue
        cur_txt, s, e = found
        try: cur = json.loads(cur_txt)
        except Exception as ex:
            report.append((name, 'SKIP', 'existing object is not parseable: %s' % str(ex)[:40])); continue
        new = json.load(open(path))
        preserved = sorted(set(cur) - set(new))
        added     = sorted(set(new) - set(cur))
        changed   = sorted(k for k in set(cur) & set(new) if cur[k] != new[k])
        merged = deep_merge(cur, new)
        kept = orphans(cur, new)
        risk = coupling_risk(cur, new)
        if risk:
            report.append((name, 'SKIP', 'stale orphan array alongside rewritten ones, not written: %s'
                           % '; '.join(risk)))
            continue
        text = text[:s] + json.dumps(merged, separators=(',', ':')) + text[e:]
        report.append((name, 'OK', 'updated %d, added %d, preserved %d  %s'
                       % (len(changed), len(added), len(kept),
                          ('(preserved: %s)' % ', '.join(kept)) if kept else '')))
    w = max(len(r[0]) for r in report)
    for n, st, msg in report: print('  %-*s %-5s %s' % (w, n, st, msg))
    if dry:
        print('\ndry run, index.html not written'); return
    if text == original:
        print('\nno change'); return
    bak = HTML + '.bak'
    shutil.copy2(HTML, bak)
    open(HTML, 'w', encoding='utf-8').write(text)
    print('\nindex.html rebuilt (%s), backup at %s' % (dt.datetime.now().strftime('%Y-%m-%d %H:%M'), os.path.basename(bak)))

if __name__ == '__main__':
    main(dry='--dry-run' in sys.argv)
