"""Annual fan charts from the empirical forecast-error distribution.

Replaces the previous hand-tuned version. The old file took quantiles of QUARTERLY
errors and averaged them across the horizons in each year:

    f = scale[v].get(y, 1.0) * (0.8 if v == 'gyy' and y > 2026 else 1.0)
    o[q].append(f * np.mean([Q(v, h, qq) for h in H]))

with scale = {'gyy': {2026: 0.35}, 'cpi': {2026: 0.3}, 'u': {2026: 0.5}}.

Two things were wrong with that. Averaging quantiles is not the quantile of the
average, and a part-forecast year was not represented, so the scale factors were
correcting both by hand. They landed within about 25% of the right answer for
2026-2028 and broke down later, where err3.pkl simply ran out of horizons.

The fix is arithmetic, not tuning. An annual average spans four quarters, so the
error in it is the SUM of that year's forecast-quarter errors divided by four,
computed per origin, with quantiles taken across origins afterwards. eval3.py now
runs to h=20 so every year through 2030 has all four quarters covered.

No scale factors. Bank Rate is an end-year value, so it takes the single Q4
horizon with no averaging.

    python bands.py
"""
import pandas as pd, numpy as np, json

R = pd.read_pickle('err3.pkl'); R = R[R.cond == False]
W = {'gyy': 0.5, 'cpi': 0.75, 'u': 0.0, 'i': 0.5}
for v, w in W.items(): R['c_' + v] = w * R[v] + (1 - w) * R['n_' + v]

YRS = [2026, 2027, 2028, 2029, 2030]
# forecast origin is 2026Q2, so 2026 has two forecast quarters and later years four
AVG_H  = {2026: [1, 2], 2027: [3, 4, 5, 6], 2028: [7, 8, 9, 10],
          2029: [11, 12, 13, 14], 2030: [15, 16, 17, 18]}
RATE_H = {2026: 2, 2027: 6, 2028: 10, 2029: 14, 2030: 18}   # the Q4 of each year
KEY = {'gyy': 'gdp', 'cpi': 'cpi', 'u': 'unemp', 'i': 'rate'}
QS = [('p05', 5), ('p25', 25), ('p75', 75), ('p95', 95)]

out = {}
for v in W:
    piv = R.pivot_table(index='T', columns='h', values='c_' + v)
    o = {q: [] for q, _ in QS}
    for y in YRS:
        if v == 'i':
            h = RATE_H[y]
            e = piv[h].dropna() if h in piv.columns else pd.Series(dtype=float)
        else:
            H = [h for h in AVG_H[y] if h in piv.columns]
            e = piv[H].sum(axis=1).dropna() / 4.0        # four quarters in the year
        for q, qq in QS:
            o[q].append(round(float(np.percentile(e, qq)), 3) if len(e) else None)
    out[KEY[v]] = o
    n = len(piv[[h for h in AVG_H[2030] if h in piv.columns]].dropna())
    print('%-6s 2030 built from %d origins' % (KEY[v], n))

print()
print(json.dumps(out, indent=0))
m = json.load(open('model_export.json'))
m['bands'] = out
m['bands_method'] = {'source': 'bands.py', 'basis': 'empirical forecast errors, annual aggregate per origin then quantiles across origins', 'scale_factors': 'none'}
json.dump(m, open('model_export.json', 'w'))
print('\nwritten to model_export.json[bands]')
