import pandas as pd, numpy as np, statsmodels.api as sm, warnings; warnings.filterwarnings('ignore')
from statsmodels.tsa.filters.hp_filter import hpfilter
RAW=pd.read_csv('uk_quarterly.csv',index_col=0); RAW.index=pd.PeriodIndex(RAW.index,freq='Q')
COV=set(pd.period_range('2020Q1','2021Q4',freq='Q')); COV2=set(pd.period_range('2020Q1','2022Q2',freq='Q'))
L=lambda s,k=1: s.shift(k)
RG=-0.07      # calibrated: real-rate gap effect on output gap (BoE transmission)
OILD=-0.003   # calibrated: y/y oil % effect on output gap (real income)
# ONESIDED: estimate the trends (gap, r*, u*, potential) using only data up to each
# point, rather than smoothing across the whole sample. The two-sided HP filter is least
# reliable at the end of the sample, which is exactly where the forecast starts, so the
# gap seeding every simulation is the worst-estimated point in the series. Default False
# keeps the published baseline; flip it and re-run eval3.py to see what it costs.
ONESIDED = False

def _hp1(x, lam):
    """One-sided HP: value at t uses only data to t. Needs a burn-in before it settles."""
    v = pd.Series(index=x.index, dtype=float)
    for i in range(len(x)):
        if i < 8: v.iloc[i] = x.iloc[:i+1].mean()
        else:     v.iloc[i] = hpfilter(x.iloc[:i+1], lam)[1].iloc[-1]
    return v

def _trend(x, lam):
    return _hp1(x, lam) if ONESIDED else hpfilter(x, lam)[1]

def prep(d):
    d=d.copy()
    lvl=np.log((1+d.g/100).cumprod())*100
    l2=lvl.where(~d.index.isin(COV)).interpolate(); tr=_trend(l2,1600)
    d['gap']=lvl-tr; d['gpot']=tr.diff()
    d['lo']=np.log(d.oil)*100; d['lfx']=np.log(d.usdgbp)*100
    d['doil']=d.lo-L(d.lo,4); d['dfx']=d.lfx-L(d.lfx,4)
    d['qo']=d.lo.diff(); d['qfx']=d.lfx.diff(); rq=(np.log(d.he)*100).diff(); rq=rq-rq.groupby(d.index.quarter).transform('mean')+rq.mean(); d['qhe']=rq; d['lhe']=rq.fillna(0).cumsum()+np.log(d.he.iloc[0])*100
    d['lp']=np.log(d.p)*100; dp=d.lp.diff()
    d['sq']=pd.Series(d.index.quarter,index=d.index)
    d['dp']=dp-dp.groupby(d.sq).transform('mean')+dp.mean()   # SA q/q %
    d['rr']=d.i-d.cpi
    d['rstar']=_trend(d.rr.where(~d.index.isin(COV)).interpolate(),10000)
    d['ustar']=_trend(d.u.where(~d.index.isin(COV)).interpolate(),1600)
    return d
def ols(y,X,keep):
    s=pd.concat([y.rename('y'),X],axis=1).dropna(); s=s.loc[[p for p in s.index if keep(p)]]
    return sm.OLS(s.y,s.drop(columns='y')).fit()
def pcX(d):
    return pd.DataFrame({'dp1':L(d.dp)-0.5,'dp2':L(d.dp,2)-0.5,'ug1':L(d.u-d.ustar),
        'qo0':d.qo,'qo1':L(d.qo),'qo2':L(d.qo,2),'qo3':L(d.qo,3),'qhe0':d.qhe,'qhe1':L(d.qhe),'qfx1':L(d.qfx),'qfx2':L(d.qfx,2),'qfx3':L(d.qfx,3),'qfx4':L(d.qfx,4)})
def fit(d):
    m={}
    m['pc']=ols(d.dp-0.5,pcX(d),lambda p:p not in COV)
    X=pd.DataFrame({'gap1':L(d.gap),'gap2':L(d.gap,2)})
    m['is']=ols(d.gap-RG*L(d.rr-d.rstar,2)-OILD*L(d.doil),X,lambda p:p not in COV2)
    X=pd.DataFrame({'i1':L(d.i),'pi':d.cpi,'gap':d.gap,'rstar':d.rstar}); X['const']=1.0
    m['tr']=ols(d.i,X,lambda p:p<=pd.Period('2008Q3') or p>=pd.Period('2022Q1'))
    X=pd.DataFrame({'du1':L(d.u.diff()),'gg':d.g-d.gpot,'gg1':L(d.g-d.gpot)})
    m['ok']=ols(d.u.diff(),X,lambda p:p not in COV2)
    return m
def simulate(m,d,H,lo=None,lfx=None,lhe=None,addf=None,gaf=None):
    T=d.index[-1]; idx=pd.period_range(T+1,T+H,freq='Q')
    e=pd.concat([d,pd.DataFrame(index=idx)])
    for c in ['rstar','ustar','gpot']: e[c]=e[c].ffill()
    e.loc[idx,'lo']=d.lo.iloc[-1] if lo is None else lo
    e.loc[idx,'lfx']=d.lfx.iloc[-1] if lfx is None else lfx
    e.loc[idx,'lhe']=d.lhe.iloc[-1] if lhe is None else lhe
    e['doil']=e.lo-L(e.lo,4); e['dfx']=e.lfx-L(e.lfx,4); e['qo']=e.lo.diff(); e['qfx']=e.lfx.diff(); e['qhe']=e.lhe.diff()
    seas=(d.lp.diff()-d.dp).groupby(d.sq).mean()
    pc,is_,tr,ok=m['pc'].params,m['is'].params,m['tr'].params,m['ok'].params
    for p in idx:
        gap=is_.gap1*e.gap.shift(1)[p]+is_.gap2*e.gap.shift(2)[p]+RG*(e.i-e.cpi-e.rstar).shift(2)[p]+OILD*e.doil.shift(1)[p]+(0 if gaf is None else gaf.get(p,0))
        e.loc[p,'gap']=gap
        x=pcX(e).loc[p]; dp=0.5+(pc*x[pc.index]).sum()+(0 if addf is None else addf.get(p,0))
        e.loc[p,'dp']=dp; e.loc[p,'lp']=e.lp.shift(1)[p]+dp+seas[p.quarter]
        e.loc[p,'cpi']=(np.exp((e.lp[p]-e.lp.shift(4)[p])/100)-1)*100
        e.loc[p,'g']=e.gpot[p]+gap-e.gap.shift(1)[p]
        du=ok.du1*(e.u.shift(1)[p]-e.u.shift(2)[p])+ok.gg*(e.g[p]-e.gpot[p])+ok.gg1*(e.g.shift(1)[p]-e.gpot.shift(1)[p])
        e.loc[p,'u']=e.u.shift(1)[p]+du
        i=tr.i1*e.i.shift(1)[p]+tr.pi*e.cpi[p]+tr.gap*gap+tr.rstar*e.rstar[p]+tr.const
        e.loc[p,'i']=max(i,0.1)
    return e
def gyy(e): l=(1+e.g/100).cumprod(); return (l/l.shift(4)-1)*100
if __name__=='__main__':
    m=fit(prep(RAW))
    for k,v in m.items():
        print('=====',k,'R2',round(v.rsquared,3),'SE',round(np.sqrt(v.scale),3),'n',int(v.nobs))
        print(pd.DataFrame({'coef':v.params.round(4),'t':v.tvalues.round(2)}).T.to_string())
