# Is the kink coefficient stable in real time, or is it identified by 2022-23 alone?
import sys; sys.path.insert(0,'data2')
from bt2 import *
import pandas as pd, numpy as np
rows=[]
for T in pd.period_range('2008Q4','2026Q2',freq='Q'):
    if T not in RAW.index: continue
    try:
        d=prepx(RAW.loc[:T]); m=fitw(d)
        rows.append({'T':str(T),'hi':float(m['wh'].params['hi']),'t_hi':float(m['wh'].tvalues['hi']),
                     'cpi1':float(m['w'].params['cpi1']),'t_cpi1':float(m['w'].tvalues['cpi1']),'n':int(m['wh'].nobs)})
    except Exception as ex: pass
R=pd.DataFrame(rows)
print("Wage-equation inflation coefficient, estimated on data available at each origin")
print("%-8s %8s %7s %9s %7s %5s" % ('origin','hi','t','cpi1(lin)','t','n'))
for _,r in R.iloc[::4].iterrows():
    print("%-8s %8.4f %7.2f %9.4f %7.2f %5d" % (r['T'],r['hi'],r['t_hi'],r['cpi1'],r['t_cpi1'],r['n']))
print("%-8s %8.4f %7.2f %9.4f %7.2f %5d" % (R.iloc[-1]['T'],R.iloc[-1]['hi'],R.iloc[-1]['t_hi'],R.iloc[-1]['cpi1'],R.iloc[-1]['t_cpi1'],R.iloc[-1]['n']))
neg=R[R.hi<0]; pos=R[R.hi>0]
print()
print("hi NEGATIVE at %d of %d origins (%s to %s)" % (len(neg),len(R),neg['T'].iloc[0] if len(neg) else '-',neg['T'].iloc[-1] if len(neg) else '-'))
print("hi POSITIVE at %d of %d origins (%s to %s)" % (len(pos),len(R),pos['T'].iloc[0] if len(pos) else '-',pos['T'].iloc[-1] if len(pos) else '-'))
if len(neg) and len(pos):
    flip=R[R.hi>0].iloc[0]
    print("sign flips at origin %s, i.e. once the 2022-23 surge is in the estimation sample" % flip['T'])
R.to_csv('kink_stability.csv',index=False); print("\nwritten to kink_stability.csv")
