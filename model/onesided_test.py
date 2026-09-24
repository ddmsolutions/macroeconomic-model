# Does removing look-ahead bias from the trend estimates help or hurt out-of-sample?
# Every 4th origin, to keep the one-sided filter's cost manageable.
import sys, time; sys.path.insert(0,'data2')
import m2, pandas as pd, numpy as np
rm=lambda x: float(np.sqrt((np.asarray(x)**2).mean()))
origins=[p for p in pd.period_range('2006Q4','2025Q2',freq='Q')
         if not (pd.Period('2019Q1')<=p<=pd.Period('2021Q4'))][::4]
res={}
for mode in (False,True):
    m2.ONESIDED=mode; t0=time.time(); rows=[]
    act=m2.prep(m2.RAW); act['gyy']=m2.gyy(act)
    for T in origins:
        d=m2.prep(m2.RAW.loc[:T]); mm=m2.fit(d); H=8
        e=m2.simulate(mm,d,H); e['gyy']=m2.gyy(e)
        for h in (4,8):
            tp=T+h
            if tp>m2.RAW.index[-1] or tp in m2.COV2: continue
            rows.append({'h':h,**{v:e.loc[tp,v]-act.loc[tp,v] for v in ['gyy','cpi','u','i']}})
    R=pd.DataFrame(rows); res[mode]=R
    print('%-10s %d origins, %.0fs' % ('one-sided' if mode else 'two-sided',len(origins),time.time()-t0))
print()
print('%-6s %-4s %10s %10s %9s' % ('var','h','two-sided','one-sided','change'))
for v in ['gyy','cpi','u','i']:
    for h in (4,8):
        a=rm(res[False][res[False].h==h][v]); b=rm(res[True][res[True].h==h][v])
        print('%-6s %-4d %10.3f %10.3f %+8.1f%%' % (v,h,a,b,(b-a)/a*100))
