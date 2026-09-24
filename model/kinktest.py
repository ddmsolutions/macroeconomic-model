# Does the kink fail because the wage equation is wrong, or because the model's
# inflation forecast is wrong? Three ways of feeding the kink:
#   hi       kink on the model's own evolving CPI forecast  (current behaviour)
#   hi-anch  kink on the last OBSERVED CPI at the origin, held flat  (usable in real time)
#   hi-act   kink on ACTUAL realised CPI  (diagnostic only, not a forecast)
import sys; sys.path.insert(0,'data2')
from bt2 import *
import pandas as pd, numpy as np
rm=lambda x: float(np.sqrt((np.asarray(x)**2).mean()))
origins=[p for p in pd.period_range('2006Q4','2025Q2',freq='Q') if not (pd.Period('2019Q1')<=p<=pd.Period('2021Q4'))]
rows=[]
for T in origins:
    d=prepx(RAW.loc[:T]); m=fitw(d); H=8; idx=pd.period_range(T+1,T+H,freq='Q')
    anch=pd.Series({p:act.cpi[T] for p in pd.period_range(T,T+H,freq='Q')})
    actc=pd.Series({p:act.cpi.get(p,np.nan) for p in pd.period_range(T,T+H,freq='Q')}).ffill()
    for nm,kc in [('hi',None),('hi-anch',anch),('hi-act',actc)]:
        e=simw(m,d,H,wage='hi',kcpi=kc)
        for h in (4,8):
            tp=T+h
            if tp>RAW.index[-1] or tp in COV2: continue
            rows.append({'T':T,'h':h,'v':nm,'err':e.loc[tp,'cpi']-act.loc[tp,'cpi'],
                         'perr':e.loc[tp,'pay']-act.loc[tp,'pay'],'pnaive':act.loc[T,'pay']-act.loc[tp,'pay']})
R=pd.DataFrame(rows)
print("CPI RMSE"); print(R.groupby(['v','h']).err.apply(rm).round(3).unstack().to_string())
print(); print("PAY RMSE  (naive: h4 %.3f  h8 %.3f)" % (rm(R[R.h==4].pnaive),rm(R[R.h==8].pnaive)))
print(R.groupby(['v','h']).perr.apply(rm).round(3).unstack().to_string())
print()
print("2022 back-test, pay path from origin 2021Q4")
T=pd.Period('2021Q4'); d=prepx(RAW.loc[:T]); m=fitw(d); H=12; idx=pd.period_range(T+1,T+H,freq='Q')
g=lambda c: pd.Series([act[c].get(p,np.nan) for p in idx]).ffill().values
anch=pd.Series({p:act.cpi[T] for p in pd.period_range(T,T+H,freq='Q')})
actc=pd.Series({p:act.cpi.get(p,np.nan) for p in pd.period_range(T,T+H,freq='Q')}).ffill()
print("  %-9s %s" % ('actual',[round(x,1) for x in act.loc[idx,'pay'].tolist()]))
for nm,kc in [('hi',None),('hi-anch',anch),('hi-act',actc)]:
    e=simw(m,d,H,g('lo'),g('lfx'),g('lhe'),'hi',kcpi=kc)
    print("  %-9s %s   CPI %s" % (nm,[round(x,1) for x in e.loc[idx,'pay'].tolist()],[round(x,1) for x in e.loc[idx,'cpi'].tolist()]))
print("  CPI at origin 2021Q4: %.1f  -> kink term max(0,cpi-4) = %.2f" % (act.cpi[T],max(0,act.cpi[T]-4)))
