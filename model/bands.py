import pandas as pd, numpy as np, json
R=pd.read_pickle('err3.pkl'); R=R[R.cond==False]
W={'gyy':0.5,'cpi':0.75,'u':0.0,'i':0.5}
for v,w in W.items(): R['c_'+v]=w*R[v]+(1-w)*R['n_'+v]
Q=lambda v,h,q: float(np.quantile(R[R.h==min(h,12)]['c_'+v],q))
yrs=[2026,2027,2028,2029,2030]
hs={2026:[2],2027:[3,4,5,6],2028:[7,8,9,10],2029:[11,12],2030:[12]}
rate_h={2026:[1],2027:[6],2028:[10],2029:[12],2030:[12]}
scale={'gyy':{2026:0.35},'cpi':{2026:0.3},'u':{2026:0.5},'i':{}}
key={'gyy':'gdp','cpi':'cpi','u':'unemp','i':'rate'}
out={}
for v in W:
    o={q:[] for q in ['p05','p25','p75','p95']}
    for y in yrs:
        H=rate_h[y] if v=='i' else hs[y]
        f=scale[v].get(y,1.0)*(0.8 if v=='gyy' and y>2026 else 1.0)
        for q,qq in [('p05',0.05),('p25',0.25),('p75',0.75),('p95',0.95)]:
            o[q].append(round(f*np.mean([Q(v,h,qq) for h in H]),3))
    out[key[v]]=o
print(json.dumps(out,indent=0))
m=json.load(open('model_export.json')); m['bands']=out; json.dump(m,open('model_export.json','w'))
