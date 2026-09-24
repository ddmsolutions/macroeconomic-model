import pandas as pd, numpy as np, sys
sys.path.insert(0,'data2')
from m2 import *
from series import load
S=load(); S.index=pd.PeriodIndex(S.index,freq='Q')
def prepx(raw):
    d=prep(raw); d=d.join(S.loc[:raw.index[-1]]); d['dinact']=d.inact-L(d.inact,4); return d
EX=lambda p: p not in COV
def fitw(d):
    m=fit(d)
    Xp=pcX(d); Xp['wg1']=L(d.pay)-3.5
    m['pcw']=ols(d.dp-0.5,Xp,EX)
    X=pd.DataFrame({'const':1.0,'w1':L(d.pay),'cpi1':L(d.cpi),'ug1':L(d.u-d.ustar),'dinact':L(d.dinact)})
    m['w']=ols(d.pay,X,EX)
    # kinked variant: wages respond to inflation only above 4%, as in est_final.py
    Xh=pd.DataFrame({'const':1.0,'w1':L(d.pay),'hi':np.maximum(0,L(d.cpi)-4),'ug1':L(d.u-d.ustar),'dinact':L(d.dinact)})
    m['wh']=ols(d.pay,Xh,EX)
    return m
def simw(m,d,H,lo=None,lfx=None,lhe=None,wage=True,addf=None,gaf=None,kcpi=None):
    T=d.index[-1]; idx=pd.period_range(T+1,T+H,freq='Q')
    e=pd.concat([d,pd.DataFrame(index=idx)])
    for c in ['rstar','ustar','gpot']: e[c]=e[c].ffill()
    e.loc[idx,'lo']=d.lo.iloc[-1] if lo is None else lo
    e.loc[idx,'lfx']=d.lfx.iloc[-1] if lfx is None else lfx
    e.loc[idx,'lhe']=d.lhe.iloc[-1] if lhe is None else lhe
    e.loc[idx,'dinact']=0.0
    e['doil']=e.lo-L(e.lo,4); e['qo']=e.lo.diff(); e['qfx']=e.lfx.diff(); e['qhe']=e.lhe.diff()
    seas=(d.lp.diff()-d.dp).groupby(d.sq).mean()
    pc=(m['pcw'] if wage else m['pc']).params; is_,tr,ok=m['is'].params,m['tr'].params,m['ok'].params
    w=m['wh' if wage=='hi' else 'w'].params
    for p in idx:
        gap=is_.gap1*e.gap.shift(1)[p]+is_.gap2*e.gap.shift(2)[p]+RG*(e.i-e.cpi-e.rstar).shift(2)[p]+OILD*e.doil.shift(1)[p]+(0 if gaf is None else gaf.get(p,0))
        e.loc[p,'gap']=gap
        # the kink reads kcpi when supplied (realised inflation), else the model's own forecast
        kc = e.cpi.shift(1)[p] if kcpi is None else float(kcpi.get(p-1, e.cpi.shift(1)[p]))
        infl = max(0.0,kc-4) if 'hi' in w.index else e.cpi.shift(1)[p]
        pw=w.const+w.w1*e.pay.shift(1)[p]+w[('hi' if 'hi' in w.index else 'cpi1')]*infl+w.ug1*(e.u-e.ustar).shift(1)[p]+w.dinact*e.dinact.shift(1)[p]
        e.loc[p,'pay']=pw
        x=pcX(e).loc[p]
        dp=0.5+(pc[[c for c in pc.index if c!='wg1']]*x[[c for c in pc.index if c!='wg1']]).sum()+(pc.get('wg1',0)*(e.pay.shift(1)[p]-3.5))+(0 if addf is None else addf.get(p,0))
        e.loc[p,'dp']=dp; e.loc[p,'lp']=e.lp.shift(1)[p]+dp+seas[p.quarter]
        e.loc[p,'cpi']=(np.exp((e.lp[p]-e.lp.shift(4)[p])/100)-1)*100
        e.loc[p,'g']=e.gpot[p]+gap-e.gap.shift(1)[p]
        du=ok.du1*(e.u.shift(1)[p]-e.u.shift(2)[p])+ok.gg*(e.g[p]-e.gpot[p])+ok.gg1*(e.g.shift(1)[p]-e.gpot.shift(1)[p])
        e.loc[p,'u']=e.u.shift(1)[p]+du
        e.loc[p,'i']=max(tr.i1*e.i.shift(1)[p]+tr.pi*e.cpi[p]+tr.gap*gap+tr.rstar*e.rstar[p]+tr.const,0.1)
    return e
act=prepx(RAW)
if __name__=='__main__':
    # 2022 back-test from 2021Q4, conditional on actual energy and sterling
    T=pd.Period('2021Q4'); d=prepx(RAW.loc[:T]); m=fitw(d); H=12; idx=pd.period_range(T+1,T+H,freq='Q')
    g=lambda c: pd.Series([act[c].get(p,np.nan) for p in idx]).ffill().values
    for wage in (False,True,'hi'):
        e=simw(m,d,H,g('lo'),g('lfx'),g('lhe'),wage)
        nm={False:'base',True:'wage-lin','hi':'wage-hi'}[wage]
        print('%-9s'%nm, 'CPI', e.loc[idx,'cpi'].round(1).tolist(), 'pay', e.loc[idx,'pay'].round(1).tolist())
    print('actual CPI',act.loc[idx,'cpi'].tolist()); print('actual pay',act.loc[idx,'pay'].tolist())
    # rolling out-of-sample CPI errors
    origins=[p for p in pd.period_range('2006Q4','2025Q2',freq='Q') if not (pd.Period('2019Q1')<=p<=pd.Period('2021Q4'))]
    rows=[]
    for T in origins:
        d=prepx(RAW.loc[:T]); m=fitw(d); H=8; idx=pd.period_range(T+1,T+H,freq='Q')
        for wage in (False,True,'hi'):
            e=simw(m,d,H,wage=wage)
            nm={False:'base',True:'lin','hi':'hi'}[wage]
            for h in (4,8):
                tp=T+h
                if tp>RAW.index[-1] or tp in COV2: continue
                rows.append({'T':T,'h':h,'wage':nm,'err':e.loc[tp,'cpi']-act.loc[tp,'cpi'],'perr':e.loc[tp,'pay']-act.loc[tp,'pay'],'pnaive':act.loc[T,'pay']-act.loc[tp,'pay']})
    R=pd.DataFrame(rows); rm=lambda x: np.sqrt((x**2).mean())
    print()
    print('CPI RMSE by wage spec')
    print(R.groupby(['wage','h']).err.apply(rm).round(3).unstack().to_string())
    print()
    print('PAY RMSE, model vs naive (naive = last observed pay carried forward)')
    pv=R[R.wage!='base'].groupby(['wage','h']).perr.apply(rm).round(3).unstack()
    pv['naive_h4']=R.groupby('h').pnaive.apply(rm).round(3)[4]
    pv['naive_h8']=R.groupby('h').pnaive.apply(rm).round(3)[8]
    print(pv.to_string())
    print()
    for sp in ('lin','hi'):
        a=rm(R[(R.wage==sp)&(R.h==4)].perr); b=rm(R[(R.wage==sp)&(R.h==8)].perr)
        na=rm(R[R.h==4].pnaive); nb=rm(R[R.h==8].pnaive)
        print('%-4s beats naive on pay:  h=4 %s (%.3f vs %.3f)   h=8 %s (%.3f vs %.3f)' % (
            sp,'YES' if a<na else 'no ',a,na,'YES' if b<nb else 'no ',b,nb))
    R.to_pickle('err_w.pkl')
