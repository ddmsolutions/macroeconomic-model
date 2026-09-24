import pandas as pd,numpy as np,statsmodels.api as sm,json
from rpi_raw import *
from m2 import RAW,COV
def q(txt):
    return pd.Series({pd.Period(l.split(',')[0].replace(' ',''),'Q'):float(l.split(',')[1]) for l in txt.strip().splitlines()})
d=RAW.copy(); d['rpi']=q(RPI); d['rpix']=q(RPIX); d['mip']=q(MIP)
d['wm']=[WM[p.year]/1000 for p in d.index]
# identity check
d['rpi_hat']=(1-d.wm)*d.rpix+d.wm*d.mip
print('identity RMSE',round(float(np.sqrt(((d.rpi_hat-d.rpi)**2).mean())),3))
# MIPs: log change in (Bank Rate smoothed + margin); try smoothing lengths
L=lambda s,k=1:s.shift(k)
best=None
for n in [1,2,4,6,8,10,12]:
    for mgn in [1.0,1.5,2.0,2.5]:
        eff=d.i.rolling(n).mean()+mgn
        x=(np.log(eff)-np.log(L(eff,4)))*100
        s=pd.concat([d.mip,x.rename('x')],axis=1).dropna()
        s=s[s.index>=pd.Period('1994Q1')]
        r=sm.OLS(s.mip,sm.add_constant(s.x)).fit()
        if best is None or r.rsquared>best[0]: best=(r.rsquared,n,mgn,r.params.values,np.sqrt(r.scale))
print('MIP best R2 %.3f n=%d margin=%.1f params=%s se=%.2f'%best[:3]+'' if False else best)
# wedge RPIX-CPI: AR(1) mean reversion
d['w']=d.rpix-d.cpi
s=pd.concat([d.w,L(d.w).rename('w1')],axis=1).dropna(); s=s.loc[[p for p in s.index if p not in COV]]
r=sm.OLS(s.w,sm.add_constant(s.w1)).fit(); print('wedge AR',r.params.round(3).to_dict(),'LR mean',round(r.params.const/(1-r.params.w1),2),'se',round(np.sqrt(r.scale),3))
print(d[['cpi','rpix','w','rpi','mip','i']].tail(8))
json.dump({'mip':{'n':int(best[1]),'mgn':float(best[2]),'c':float(best[3][0]),'b':float(best[3][1]),'r2':float(best[0]),'se':float(best[4])},
 'w':{'c':float(r.params.const),'rho':float(r.params.w1),'se':float(np.sqrt(r.scale)),'r2':float(r.rsquared)},
 'hist':{'q':[str(p) for p in d.index[-12:]],'i':d.i.iloc[-12:].round(4).tolist(),'w':d.w.iloc[-12:].round(3).tolist(),'rpi':d.rpi.iloc[-12:].tolist(),'mip':d.mip.iloc[-12:].tolist(),'rpix':d.rpix.iloc[-12:].tolist()},
 'wm':WM[2026]/1000,'wd':WD[2026]/1000},open('rpi_export.json','w'))
