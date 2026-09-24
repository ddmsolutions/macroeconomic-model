"""Do commodities other than crude belong in this model?

Four candidates, and they are not the same kind of question.

  petrol   CPI motor fuels is close to an identity: pump price is crude in sterling plus
           duty plus VAT. Should be strongly predictable and worth having.
  gas      European wholesale gas is the input behind the Ofgem cap and so behind the
           household energy series the model currently ASSUMES. If gas leads energy CPI
           with a usable lag, the biggest hand-set assumption becomes a forecast.
  gold     a dollar asset driven by global real yields. A UK quarterly model has no
           obvious information advantage. Tested rather than assumed.
  silver   gold plus industrial demand, so in principle more cyclical.

Every claim is tested against a random walk on the same sample. Nothing goes in on
plausibility.

    python commodities.py
"""
import os, glob, json
import numpy as np, pandas as pd, statsmodels.api as sm
import warnings; warnings.filterwarnings('ignore')

HERE = os.path.dirname(os.path.abspath(__file__))
V = sorted(glob.glob(os.path.join(HERE, 'data', 'vintages', '*')))[-1]

def ser(name):
    fp = os.path.join(V, name + '.csv')
    if not os.path.exists(fp): return None
    s = pd.read_csv(fp, index_col=0)['value']; s.index = pd.PeriodIndex(s.index, freq='Q')
    return s[~s.index.duplicated()]

D = {n: ser(n) for n in ['fuel','oil','usdgbp','he_yoy','elec','gas_r','gas_eu','gold','silver','cpi','i','u','g']}
d = pd.DataFrame({k: v for k, v in D.items() if v is not None}).sort_index()
L = lambda s, k=1: s.shift(k)
yoy = lambda s: (s / s.shift(4) - 1) * 100

# crude in sterling: what a UK forecourt actually faces
d['oil_gbp'] = d.oil / d.usdgbp
d['doil_gbp'] = yoy(d.oil_gbp)
d['dgas_eu'] = yoy(d.gas_eu)
d['dgold'] = yoy(d.gold)
d['dsilver'] = yoy(d.silver)

def run(y, X, label, sample=None):
    s = pd.concat([y.rename('y'), X], axis=1).dropna()
    if sample is not None: s = s.loc[[p for p in s.index if p >= sample]]
    if len(s) < 30: return None
    r = sm.OLS(s.y, sm.add_constant(s.drop(columns='y'))).fit()
    rw = float(np.sqrt(((s.y - s.y.shift(1)).dropna() ** 2).mean()))
    print('  %-34s R2 %.3f  se %.2f  n %-4d  random-walk se %.2f  %s'
          % (label, r.rsquared, np.sqrt(r.scale), int(r.nobs), rw,
             'BEATS RW' if np.sqrt(r.scale) < rw else 'loses to RW'))
    return r

S = pd.Period('1997Q1', 'Q')
print('sample from %s, vintage %s\n' % (S, os.path.basename(V)))

print('PETROL  CPI motor fuels (07.2.2) annual rate')
run(d.fuel, pd.DataFrame({'doil_gbp': d.doil_gbp}), 'on sterling crude, contemporaneous', S)
run(d.fuel, pd.DataFrame({'doil_gbp': d.doil_gbp, 'l1': L(d.doil_gbp)}), 'plus one lag', S)
r_fuel = run(d.fuel, pd.DataFrame({'doil_gbp': d.doil_gbp, 'l1': L(d.doil_gbp), 'f1': L(d.fuel)}), 'plus own lag', S)

print('\nGAS  does European wholesale gas lead UK household energy CPI?')
for k in range(0, 5):
    run(d.he_yoy, pd.DataFrame({'g': L(d.dgas_eu, k)}), 'energy CPI on gas lagged %dq' % k, S)
r_gas = run(d.he_yoy, pd.DataFrame({'g1': L(d.dgas_eu), 'g2': L(d.dgas_eu, 2), 'h1': L(d.he_yoy)}),
            'gas lags 1-2 plus own lag', S)

print('\nGOLD  can a UK macro model say anything? real rate = Bank Rate minus CPI')
d['rr'] = d.i - d.cpi
run(d.dgold, pd.DataFrame({'rr': L(d.rr)}), 'gold y/y on lagged UK real rate', S)
run(d.dgold, pd.DataFrame({'rr': L(d.rr), 'dg1': L(d.dgold)}), 'plus own lag', S)
run(d.dgold, pd.DataFrame({'rr': L(d.rr), 'cpi': L(d.cpi), 'fx': L(yoy(d.usdgbp))}), 'real rate, CPI, sterling', S)

print('\nSILVER  same, plus the output gap as an industrial-demand proxy')
run(d.dsilver, pd.DataFrame({'rr': L(d.rr)}), 'silver y/y on lagged UK real rate', S)
run(d.dsilver, pd.DataFrame({'rr': L(d.rr), 'g': L(d.g)}), 'plus UK GDP growth', S)
run(d.dsilver, pd.DataFrame({'rr': L(d.rr), 'dgold': L(d.dgold)}), 'plus lagged gold', S)

print('\nREVERSE  do gold and silver help forecast UK CPI?')
base = run(d.cpi, pd.DataFrame({'c1': L(d.cpi), 'c2': L(d.cpi, 2)}), 'CPI on own lags (baseline)', S)
run(d.cpi, pd.DataFrame({'c1': L(d.cpi), 'c2': L(d.cpi, 2), 'dg': L(d.dgold)}), 'plus lagged gold', S)
run(d.cpi, pd.DataFrame({'c1': L(d.cpi), 'c2': L(d.cpi, 2), 'ds': L(d.dsilver)}), 'plus lagged silver', S)
run(d.cpi, pd.DataFrame({'c1': L(d.cpi), 'c2': L(d.cpi, 2), 'gg': L(d.dgas_eu)}), 'plus lagged European gas', S)
