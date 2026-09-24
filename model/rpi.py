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
# Mortgage interest payments: log change in an effective mortgage rate, modelled as a
# blend of a short and a long moving average of Bank Rate plus a lender margin.
#
# This mirrors index.html exactly, which computes
#     eff = mip.a * ma(4) + (1 - mip.a) * ma(mip.n2) + mip.mgn
# Previously this script grid-searched a SINGLE smoothing length while the page used the
# two-horizon blend, so the fitted c and b described a different model from the one being
# rendered. Exporting them over the page's a and n2 produced an incoherent mixture.
L=lambda s,k=1:s.shift(k)
best=None
for a in [0.2,0.3,0.4,0.5,0.6,0.7]:
    for n2 in [12,16,20,24,28,32]:
        for mgn in [1.0,1.5,2.0,2.5,3.0]:
            eff=a*d.i.rolling(4).mean()+(1-a)*d.i.rolling(n2).mean()+mgn
            x=(np.log(eff)-np.log(L(eff,4)))*100
            s=pd.concat([d.mip,x.rename('x')],axis=1).dropna()
            s=s[s.index>=pd.Period('1994Q1')]
            if len(s)<40: continue
            r=sm.OLS(s.mip,sm.add_constant(s.x)).fit()
            if best is None or r.rsquared>best[0]:
                best=(r.rsquared,a,n2,mgn,r.params.values,np.sqrt(r.scale),int(r.nobs))
print('MIP best: R2 %.3f  a=%.1f  n2=%d  margin=%.1f  se=%.2f  n=%d'%(best[0],best[1],best[2],best[3],best[5],best[6]))
# wedge RPIX-CPI: AR(1) mean reversion
d['w']=d.rpix-d.cpi
s=pd.concat([d.w,L(d.w).rename('w1')],axis=1).dropna(); s=s.loc[[p for p in s.index if p not in COV]]
r=sm.OLS(s.w,sm.add_constant(s.w1)).fit(); print('wedge AR',r.params.round(3).to_dict(),'LR mean',round(r.params.const/(1-r.params.w1),2),'se',round(np.sqrt(r.scale),3))
print(d[['cpi','rpix','w','rpi','mip','i']].tail(8))
# w0: the RPIX-CPI wedge at the jumping-off point. index.html seeds its wedge recursion
# with this, and it was hand-held in the HTML, so it silently aged every quarter.
W0=float(d.w.dropna().iloc[-1])

# cpih_gap: index.html approximates CPIH as cpi + cpih_gap when building RPI. That was a
# hand-set 0.2. The gap is observable and is NOT constant: over the last three years it has
# run from -0.4 to +0.9, driven by owner-occupier housing costs, which CPIH includes and CPI
# does not. The latest reading is exported, and the recent range with it so the page can
# show how uncertain a constant is.
CPIH_GAP=None; CPIH_RANGE=None
try:
    import glob, os
    vs=sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),'data','vintages','*','cpih.csv')))
    if vs:
        ch=pd.read_csv(vs[-1],index_col=0)['value']; ch.index=pd.PeriodIndex(ch.index,freq='Q')
        gap=(ch-d.cpi).dropna()
        CPIH_GAP=round(float(gap.iloc[-1]),2)
        _g12=gap.iloc[-12:]; CPIH_RANGE=[round(float(_g12.min()),2),round(float(_g12.max()),2),round(float(_g12.mean()),2)]
        print('CPIH-CPI gap: latest %.2f  last 12q min/max/mean %s'%(CPIH_GAP,CPIH_RANGE))
except Exception as ex:
    print('CPIH gap not derived (%s), page keeps its existing value'%str(ex)[:50])
print('wedge w0 = %.3f'%W0)

_out={'mip':{'a':float(best[1]),'n2':int(best[2]),'mgn':float(best[3]),'c':float(best[4][0]),'b':float(best[4][1]),'r2':float(best[0]),'se':float(best[5]),'n':int(best[6])},
 'w':{'c':float(r.params.const),'rho':float(r.params.w1),'se':float(np.sqrt(r.scale)),'r2':float(r.rsquared),'n':int(r.nobs)},
 # hist.cpi is required by index.html, which computes the RPIX-CPI wedge as rpix-cpi at
 # render time. It was previously hand-held in the HTML and had no generating script, so
 # regenerating hist without it left the page indexing past the end of a stale array.
 'hist':{'q':[str(p) for p in d.index[-12:]],'i':d.i.iloc[-12:].round(4).tolist(),'w':d.w.iloc[-12:].round(3).tolist(),'rpi':d.rpi.iloc[-12:].tolist(),'mip':d.mip.iloc[-12:].tolist(),'rpix':d.rpix.iloc[-12:].tolist(),'cpi':d.cpi.iloc[-12:].round(3).tolist()},
 # Bank Rate history for the MIP moving averages. index.html takes ma(j, n2) over
 # ihist concatenated with the forecast, so this must be at least n2 long or the early
 # quarters average over undefined entries. Four spare quarters of headroom.
 'ihist':d.i.iloc[-(int(best[2])+4):].round(4).tolist(),
 'wm':WM[2026]/1000,'wd':WD[2026]/1000,'w0':W0}
if CPIH_GAP is not None:
    _out['cpih_gap']=CPIH_GAP; _out['cpih_gap_range']=CPIH_RANGE
json.dump(_out,open('rpi_export.json','w'))
