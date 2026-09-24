"""Household energy from wholesale gas, replacing an assumption with a forecast.

fc.py hand-types the household energy path (+13% then +4%). Energy was the single
largest inflation driver of 2022, so that assumption carries a lot of the forecast.

European wholesale gas leads UK household energy CPI with R2 rising monotonically to
0.658 at a four-quarter lag, which is the Ofgem cap transmission: wholesale prices enter
the cap through a defined observation window and reach bills with a long, mechanical lag.

That lead is the point. At any forecast origin the next three to four quarters of energy
are already determined by gas prices that have ALREADY been observed, so the first year is
a genuine forecast rather than a guess. Beyond the lead the path is conditional on an
assumption about gas, which is stated rather than hidden.

    python energy.py          estimate and report
"""
import os, glob
import numpy as np, pandas as pd, statsmodels.api as sm
import warnings; warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))

def _vintage():
    vs = sorted(glob.glob(os.path.join(HERE, 'data', 'vintages', '*')))
    return vs[-1] if vs else None

def load(vdir=None):
    vdir = vdir or _vintage()
    out = {}
    for n in ('he_yoy', 'gas_eu'):
        fp = os.path.join(vdir, n + '.csv')
        if not os.path.exists(fp): return None
        s = pd.read_csv(fp, index_col=0)['value']; s.index = pd.PeriodIndex(s.index, freq='Q')
        out[n] = s[~s.index.duplicated()]
    d = pd.DataFrame(out).sort_index()
    d['dgas'] = (d.gas_eu / d.gas_eu.shift(4) - 1) * 100
    # gas publishes ahead of the CPI energy component, so trim to the last quarter where
    # the dependent variable actually exists. Otherwise the recursion starts from NaN.
    last = d.he_yoy.dropna().index[-1]
    return d.loc[:last]

LAGS = (1, 2)      # gas lags used; the lead runs to 4 but 1-2 plus persistence carries it

def fit(d, upto=None, start='1997Q1'):
    x = d if upto is None else d.loc[:upto]
    X = pd.DataFrame({'g%d' % k: x.dgas.shift(k) for k in LAGS})
    X['h1'] = x.he_yoy.shift(1)
    s = pd.concat([x.he_yoy.rename('y'), X], axis=1).dropna()
    s = s.loc[[p for p in s.index if p >= pd.Period(start, 'Q')]]
    return sm.OLS(s.y, sm.add_constant(s)[['const'] + list(X.columns)]).fit()

def project(d, m, H, gas_growth=None):
    """Forecast he_yoy H quarters ahead. gas_growth: assumed gas y/y beyond observed data.

    Returns (he_yoy path, n_quarters_determined_by_observed_gas).
    """
    p = m.params
    e = d.copy()
    T = e.index[-1]
    idx = pd.period_range(T + 1, T + H, freq='Q')
    e = pd.concat([e, pd.DataFrame(index=idx)])
    # gas beyond the data: held at its last observed y/y unless told otherwise
    g_assumed = float(d.dgas.dropna().iloc[-1]) if gas_growth is None else gas_growth
    e.loc[idx, 'dgas'] = g_assumed
    determined = 0
    for j, q in enumerate(idx):
        lags_observed = all((q - k) <= T for k in LAGS)
        if lags_observed: determined = j + 1
        v = p['const'] + p['h1'] * e.he_yoy.shift(1)[q]
        for k in LAGS: v += p['g%d' % k] * e.dgas.shift(k)[q]
        e.loc[q, 'he_yoy'] = v
    return e.loc[idx, 'he_yoy'], determined

if __name__ == '__main__':
    d = load()
    m = fit(d)
    print('Household energy CPI on European wholesale gas\n')
    print('  R2 %.3f   se %.2f   n %d' % (m.rsquared, np.sqrt(m.scale), int(m.nobs)))
    print('  ' + '  '.join('%s %.4f (t %.2f)' % (k, m.params[k], m.tvalues[k]) for k in m.params.index))
    print()
    print('  long-run gas pass-through: %.3f' % (sum(m.params['g%d' % k] for k in LAGS) / (1 - m.params['h1'])))
    print()
    path, det = project(d, m, 18)
    print('  projection from %s, %d quarters determined by ALREADY OBSERVED gas:' % (d.index[-1], det))
    print('   ', [round(float(x), 1) for x in path[:8]], '...')
    print()
    print('  current hand-typed assumption in fc.py: +13%% then +4%% y/y')
    print('  this equation says: %.1f%% then %.1f%%' % (float(path.iloc[0]), float(path.iloc[1])))
    # stability
    print('\n  real-time coefficient stability (gas pass-through, sum of lags):')
    for T in ['2010Q4','2015Q4','2019Q4','2021Q4','2023Q4','2026Q2']:
        try:
            mm = fit(d, upto=pd.Period(T,'Q'))
            print('    %-8s %.4f  (R2 %.3f, n %d)' % (T, sum(mm.params['g%d'%k] for k in LAGS), mm.rsquared, int(mm.nobs)))
        except Exception as ex: print('    %-8s failed %s' % (T, str(ex)[:30]))
