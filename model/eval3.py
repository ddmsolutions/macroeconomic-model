import pandas as pd, numpy as np, pickle
from m2 import *
act=prep(RAW); act['gyy']=gyy(act)
origins=[p for p in pd.period_range('2004Q4','2025Q2',freq='Q') if not (pd.Period('2019Q1')<=p<=pd.Period('2021Q4'))]
rows=[]
for T in origins:
    d=prep(RAW.loc[:T]); m=fit(d); H=20; idx=pd.period_range(T+1,T+H,freq="Q")
    for cond in (False,True):
        lo=lfx=lhe=None
        if cond:
            lo=pd.Series([act.lo.get(p,np.nan) for p in idx]).ffill().values; lfx=pd.Series([act.lfx.get(p,np.nan) for p in idx]).ffill().values; lhe=pd.Series([act.lhe.get(p,np.nan) for p in idx]).ffill().values
        e=simulate(m,d,H,lo,lfx,lhe); e['gyy']=gyy(e)
        for h in range(1,H+1):
            tp=T+h
            if tp>RAW.index[-1] or tp in COV2: continue
            r={'T':T,'h':h,'cond':cond}
            for v in ['gyy','cpi','u','i']: r[v]=e.loc[tp,v]-act.loc[tp,v]; r['n_'+v]=act.loc[T,v]-act.loc[tp,v]
            rows.append(r)
R=pd.DataFrame(rows); R.to_pickle('err3.pkl')
R['era']=np.where(R['T']<pd.Period('2019Q1'),'pre2019','post2022')
def rm(x): return np.sqrt((x**2).mean())
for cond in (False,True):
    s=R[R.cond==cond]
    print('conditional on actual oil/fx' if cond else 'unconditional (oil, fx flat)')
    for h in (4,8):
        g=s[s.h==h]
        out={}
        for v in ['gyy','cpi','u','i']:
            out[v]=(round(rm(g[v]),2),round(rm(g['n_'+v]),2),round(rm(0.5*g[v]+0.5*g['n_'+v]),2))
        print(' h',h,'(model, naive, 50/50 combo)',out)
