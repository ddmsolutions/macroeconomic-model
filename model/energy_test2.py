# Two refinements the theory suggests:
#   lags34  use gas at lags 3-4, where the fit is strongest (R2 0.63/0.66) and the lead longest
#   pinned  apply the gas forecast ONLY for quarters determined by already-observed gas,
#           and hold flat beyond, instead of extrapolating an autoregression
import sys; sys.path.insert(0,'data2')
import numpy as np, pandas as pd, statsmodels.api as sm, m2, energy
import warnings; warnings.filterwarnings('ignore')
rm=lambda x: float(np.sqrt((np.asarray(x)**2).mean()))
E=energy.load(); act=m2.prep(m2.RAW); act['gyy']=m2.gyy(act)
origins=[p for p in pd.period_range('2006Q4','2024Q2',freq='Q')
         if not (pd.Period('2019Q1')<=p<=pd.Period('2021Q4'))][::2]

def fit_lags(d,upto,lags,start='1997Q1'):
    x=d.loc[:upto]
    X=pd.DataFrame({'g%d'%k:x.dgas.shift(k) for k in lags}); X['h1']=x.he_yoy.shift(1)
    s=pd.concat([x.he_yoy.rename('y'),X],axis=1).dropna()
    s=s.loc[[p for p in s.index if p>=pd.Period(start,'Q')]]
    return sm.OLS(s.y,sm.add_constant(s)[['const']+list(X.columns)]).fit(),lags

def proj(d,m,lags,H):
    p=m.params; e=d.copy(); T=e.index[-1]
    idx=pd.period_range(T+1,T+H,freq='Q'); e=pd.concat([e,pd.DataFrame(index=idx)])
    e.loc[idx,'dgas']=float(d.dgas.dropna().iloc[-1]); det=0
    for j,q in enumerate(idx):
        if all((q-k)<=T for k in lags): det=j+1
        v=p['const']+p['h1']*e.he_yoy.shift(1)[q]
        for k in lags: v+=p['g%d'%k]*e.dgas.shift(k)[q]
        e.loc[q,'he_yoy']=v
    return e.loc[idx,'he_yoy'].values,det

def to_lhe(hist,yoy,n=None):
    lv=list(np.exp(np.asarray(hist)/100.0)); out=[]
    for j in range(len(yoy)):
        if n is not None and j>=n: out.append(out[-1] if out else np.log(lv[-1])*100.0); continue
        base=lv[-4] if len(lv)>=4 else lv[-1]; nxt=base*(1+float(yoy[j])/100.0)
        lv.append(nxt); out.append(np.log(nxt)*100.0)
    return np.array(out)

rows=[]
for T in origins:
    if T not in m2.RAW.index or T not in E.index: continue
    d=m2.prep(m2.RAW.loc[:T]); mm=m2.fit(d); H=12; idx=pd.period_range(T+1,T+H,freq='Q')
    variants={'flat':None}
    try:
        m12,l12=fit_lags(E,T,(1,2)); y12,d12=proj(E.loc[:T],m12,l12,H)
        m34,l34=fit_lags(E,T,(3,4)); y34,d34=proj(E.loc[:T],m34,l34,H)
        variants['lags12']=to_lhe(d.lhe.iloc[-8:].values,y12)
        variants['lags34']=to_lhe(d.lhe.iloc[-8:].values,y34)
        variants['pinned34']=to_lhe(d.lhe.iloc[-8:].values,y34,n=max(d34,1))
    except Exception: continue
    for tag,arg in variants.items():
        e=m2.simulate(mm,d,H,None,None,arg)
        for h in (4,8,12):
            tp=T+h
            if tp>m2.RAW.index[-1] or tp in m2.COV2: continue
            rows.append({'T':T,'h':h,'v':tag,'cpi':e.loc[tp,'cpi']-act.loc[tp,'cpi']})
R=pd.DataFrame(rows)
print('CPI RMSE by energy treatment (%d origins)\n'%R['T'].nunique())
print('%-10s %8s %8s %8s'%('variant','h=4','h=8','h=12'))
for v in ['flat','lags12','lags34','pinned34']:
    if v not in set(R.v): continue
    print('%-10s %8.3f %8.3f %8.3f'%(v,*[rm(R[(R.v==v)&(R.h==h)].cpi) for h in (4,8,12)]))
