import pandas as pd, numpy as np, json
from m2 import *
R=pd.read_pickle('err3.pkl'); R=R[R.cond==False]
rm=lambda x: float(np.sqrt((x**2).mean()))
W={};RM={}
for v in ['gyy','cpi','u','i']:
    best=None
    for w in [0,0.25,0.5,0.75,1]:
        sc=np.mean([rm(w*R[R.h==h][v]+(1-w)*R[R.h==h]['n_'+v]) for h in (4,8)])
        if best is None or sc<best[1]: best=(w,sc)
    W[v]=best[0]
    RM[v]=[round(rm(W[v]*R[R.h==h][v]+(1-W[v])*R[R.h==h]['n_'+v]),2) for h in range(1,21)]
    RM[v+'_model']=[round(rm(R[R.h==h][v]),2) for h in range(1,21)]
    RM[v+'_naive']=[round(rm(R[R.h==h]['n_'+v]),2) for h in range(1,21)]
print('weights',W); 
for k,v in RM.items(): print(k,v)
# calm-period RMSE (excl 2008-09 and 2022-23 shocks)
calm=R[~R['T'].apply(lambda p: pd.Period('2007Q2')<=p<=pd.Period('2009Q4') or pd.Period('2021Q1')<=p<=pd.Period('2023Q2'))]
CALM={v:[round(rm(W[v]*calm[calm.h==h][v]+(1-W[v])*calm[calm.h==h]['n_'+v]),2) for h in (4,8)] for v in ['gyy','cpi','u','i']}
print('calm',CALM)
# Back-test 2022: origin 2021Q4, actual oil and fx
act=prep(RAW); act['gyy']=gyy(act)
T=pd.Period('2021Q4'); d=prep(RAW.loc[:T]); m=fit(d); idx=pd.period_range(T+1,'2024Q4',freq='Q')
lo=[act.lo[p] for p in idx]; lfx=[act.lfx[p] for p in idx]; lhe=[act.lhe[p] for p in idx]
e=simulate(m,d,len(idx),lo,lfx,lhe)
e0=simulate(m,d,len(idx))
bt=pd.DataFrame({'cpi_act':act.cpi[idx],'cpi_mod':e.cpi[idx],'cpi_flat':e0.cpi[idx],'i_act':act.i[idx],'i_mod':e.i[idx],'u_act':act.u[idx],'u_mod':e.u[idx]}).round(2)
print(bt)
json.dump({'W':W,'RM':RM,'CALM':CALM,'bt':{'q':[str(p) for p in idx],**{c:bt[c].tolist() for c in bt}}},open('eval_out.json','w'))
