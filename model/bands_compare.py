# Three ways of building the annual fan, compared.
#   old   bands.py: quantile of quarterly errors, then averaged across horizons, then fudged
#   fixed the same empirical errors but aggregated in the correct order
#   stoch quantiles of simulated annual aggregates
import pandas as pd, numpy as np, json
R=pd.read_pickle('err3.pkl'); R=R[R.cond==False]
W={'gyy':0.5,'cpi':0.75,'u':0.0,'i':0.5}
for v,w in W.items(): R['c_'+v]=w*R[v]+(1-w)*R['n_'+v]
yrs=[2026,2027,2028,2029,2030]
hs={2026:[2],2027:[3,4,5,6],2028:[7,8,9,10],2029:[11,12],2030:[12]}
rate_h={2026:[1],2027:[6],2028:[10],2029:[12],2030:[12]}
scale={'gyy':{2026:0.35},'cpi':{2026:0.3},'u':{2026:0.5},'i':{}}
key={'gyy':'gdp','cpi':'cpi','u':'unemp','i':'rate'}
QS=[('p05',5),('p25',25),('p75',75),('p95',95)]

def old_way(v,y):
    H=rate_h[y] if v=='i' else hs[y]
    f=scale[v].get(y,1.0)*(0.8 if v=='gyy' and y>2026 else 1.0)
    return {q:f*np.mean([np.percentile(R[R.h==min(h,12)]['c_'+v],qq) for h in H]) for q,qq in QS}

def fixed_way(v,y):
    """Average each origin's errors across the year FIRST, then take quantiles.
    That is the quantile of the annual average, which is what the fan chart claims."""
    H=rate_h[y] if v=='i' else hs[y]
    piv=R.pivot_table(index='T',columns='h',values='c_'+v)
    cols=[h for h in H if h in piv.columns]
    ann=piv[cols].mean(axis=1).dropna()
    return {q:np.percentile(ann,qq) for q,qq in QS}

st=json.load(open('model_export.json'))['bands']
print('%-6s %-5s %8s %8s %8s   %8s %8s %8s'%('','','old p05','fixed','stoch','old p95','fixed','stoch'))
for v in ['gyy','cpi','u','i']:
    k=key[v]
    for y in yrs:
        o,f_=old_way(v,y),fixed_way(v,y); j=yrs.index(y)
        print('%-6s %-5d %8.2f %8.2f %8.2f   %8.2f %8.2f %8.2f'%(
            k if y==2026 else '',y,o['p05'],f_['p05'],st[k]['p05'][j],o['p95'],f_['p95'],st[k]['p95'][j]))
    print()
