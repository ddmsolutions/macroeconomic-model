import pandas as pd,numpy as np,statsmodels.api as sm,json
from m2 import RAW,prep,COV
d=prep(RAW)
hp=pd.Series({pd.Period(l.split(',')[0].replace(' ',''),'Q'):float(l.split(',')[1]) for l in open('hp.txt').read().split('\n') if l})
d['lh']=np.log(hp)*100; d['dh']=d.lh.diff()
L=lambda s,k=1:s.shift(k)
def ols(y,X,keep=lambda p:True):
    s=pd.concat([y.rename('y'),X],axis=1).dropna(); s=s.loc[[p for p in s.index if keep(p)]]
    return sm.OLS(s.y,sm.add_constant(s.drop(columns='y'))).fit()
noc=lambda p:p not in COV
# House prices (RPI depreciation index, a smoothed house price measure): quarterly growth
best=None
for lag in [1,2,3,4]:
    X=pd.DataFrame({'dh1':L(d.dh),'dh2':L(d.dh,2),'di':L(d.i.diff(4),lag),'rr':L(d.i-d.cpi-d.rstar,lag),'gap':L(d.gap)})
    r=ols(d.dh,X,noc)
    if best is None or r.rsquared>best[1].rsquared: best=(lag,r)
lag,rh=best; print('HOUSE lag',lag); print(pd.DataFrame({'b':rh.params.round(3),'t':rh.tvalues.round(2)}).T.to_string(),'R2',round(rh.rsquared,3))
# long-run effect of a sustained 1pp rise in Bank Rate on house price level (simulate)
p=rh.params; lvl=0; dh=[0,0]; ipath=[0]*4+[1]*40; out=[]
for t in range(4,40):
    di=ipath[t-lag]-ipath[t-lag-4]; rr=ipath[t-lag]
    x=p.dh1*dh[-1]+p.dh2*dh[-2]+p.di*di+p.rr*rr
    dh.append(x); lvl+=x; out.append(lvl)
print('house level after 4,8,12,20 qtrs of +1pp rate:',[round(out[k],2) for k in (3,7,11,19)])
# Sterling: y/y log change on y/y change in Bank Rate
X=pd.DataFrame({'di':d.i.diff(4),'di1':L(d.i.diff(4),4)})
rf=ols(d.dfx,X,noc); print('FX',rf.params.round(3).to_dict(),rf.tvalues.round(2).to_dict(),'R2',round(rf.rsquared,3))
X=pd.DataFrame({'di':d.i.diff(),'dfx1':L(d.qfx)})
rq=ols(d.qfx,X,noc); print('FX q/q',rq.params.round(3).to_dict(),rq.tvalues.round(2).to_dict(),'R2',round(rq.rsquared,3))
json.dump({'house':{'lag':lag,**{k:float(v) for k,v in rh.params.items()},'r2':float(rh.rsquared),'n':int(rh.nobs),'t':{k:float(v) for k,v in rh.tvalues.items()}},
 'fx':{**{k:float(v) for k,v in rf.params.items()},'r2':float(rf.rsquared),'t':{k:float(v) for k,v in rf.tvalues.items()}}},open('links_est.json','w'))
