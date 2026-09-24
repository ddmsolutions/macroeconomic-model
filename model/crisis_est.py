import pandas as pd,numpy as np,statsmodels.api as sm,json
from m2 import RAW,prep,COV
from crisis_raw import *
d=prep(RAW)
q=lambda s:pd.Series({pd.Period(x.split(',')[0].replace(' ',''),'Q'):float(x.split(',')[1]) for x in s.split('|')})
d['debt']=q(DEBT); d['sav']=q(SAV)
# mortgage (monthly -> quarterly)
rows=[]
for l in open('mort_raw.txt'):
    p=l.strip().split(','); y=int(p[0]); y=2000+y if y<50 else 1900+y
    for m,v in enumerate(p[1:]): rows.append((pd.Period(f"{y}-{m+1:02d}",'M'),float(v)))
mo=pd.Series(dict(rows)); d['mort']=mo.groupby(mo.index.asfreq('Q')).mean()
g=pd.read_csv('bond-yields-uk-10y_quarterly.csv',parse_dates=['Date']); g.index=g.Date.dt.to_period('Q')
gilt=g.Rate.copy()
gm={'2026Q1':(4.451+4.4324+4.7007)/3,'2026Q2':(4.8207+4.9416+4.796)/3}
for k,v in gm.items(): gilt[pd.Period(k)]=v
d['gilt']=gilt
# nominal GDP proxy (real level x CPI level) scaled so 2026Q2 annualised = 3183bn
lvl=(1+d.g/100).cumprod()*d.p; ngdp=lvl/lvl.iloc[-1]*3183
apf=pd.Series(np.nan,index=d.index); apf[:pd.Period('2008Q4')]=0
for k,v in APF.items():
    if pd.Period(k) in apf.index: apf[pd.Period(k)]=v
apf=apf.interpolate(); apf[pd.Period('2026Q3'):]=488
d['apf']=apf/ngdp*100
L=lambda s,k=1:s.shift(k)
def ols(y,X,keep=lambda p:True,const=True):
    s=pd.concat([y.rename('y'),X],axis=1).dropna(); s=s.loc[[p for p in s.index if keep(p)]]
    Xs=sm.add_constant(s.drop(columns='y')) if const else s.drop(columns='y')
    return sm.OLS(s.y,Xs).fit(cov_type='HAC',cov_kwds={'maxlags':4})
noc=lambda p:p not in COV
out={}
def show(n,r):
    print('==',n,'R2',round(r.rsquared,3),'n',int(r.nobs)); print(pd.DataFrame({'b':r.params.round(3),'t':r.tvalues.round(2)}).T.to_string())
    out[n]={'b':{k:float(v) for k,v in r.params.items()},'t':{k:float(v) for k,v in r.tvalues.items()},'r2':float(r.rsquared),'n':int(r.nobs)}
# 1 gilt yields: 4-quarter changes
X=pd.DataFrame({'di':d.i.diff(4),'ddebt':d.debt.diff(4),'dapf':d.apf.diff(4),'dcpi':d.cpi.diff(4)})
show('gilt_d4',ols(d.gilt.diff(4),X,noc))
# levels with neutral-rate trend control
X=pd.DataFrame({'i':d.i,'debt':d.debt,'apf':d.apf,'rstar':d.rstar,'cpi':d.cpi})
show('gilt_lvl',ols(d.gilt,X,noc))
# 2 mortgage spread over Bank Rate: gap and expected rate change (realised i(t+4)-i(t))
d['msp']=d.mort-d.i
X=pd.DataFrame({'gap':d.gap,'fwd':d.i.shift(-4)-d.i,'msp1':L(d.msp)})
show('mspread',ols(d.msp,X,lambda p:p not in COV and p>=pd.Period('1996Q1')))
X=pd.DataFrame({'gapneg':np.minimum(0,d.gap),'gappos':np.maximum(0,d.gap),'fwd':d.i.shift(-4)-d.i,'msp1':L(d.msp)})
show('mspread_asym',ols(d.msp,X,lambda p:p not in COV and p>=pd.Period('1996Q1')))
# 3 house prices (RPI depreciation index) on mortgage rate changes
hp=pd.Series({pd.Period(l.split(',')[0].replace(' ',''),'Q'):float(l.split(',')[1]) for l in open('hp.txt').read().split('\n') if l})
d['dh']=(np.log(hp)*100).diff()
for lag in [1,2,3,4]:
    X=pd.DataFrame({'dh1':L(d.dh),'dmort':L(d.mort.diff(4),lag),'gap':L(d.gap)})
    r=ols(d.dh,X,noc); print('house lag',lag,'dmort b',round(r.params.dmort,3),'t',round(r.tvalues.dmort,2),'dh1',round(r.params.dh1,3))
X=pd.DataFrame({'dh1':L(d.dh),'dmort':L(d.mort.diff(4),2),'gap':L(d.gap)}); rh=ols(d.dh,X,noc); show('house',rh)
lr=rh.params.dmort/(1-rh.params.dh1); print('long-run house price level per +1pp mortgage rate (sustained, 4q change counted once per q for 4q):',round(lr*4,2))
# 4 saving ratio: precautionary response to unemployment changes
X=pd.DataFrame({'sav1':L(d.sav),'du4':d.u.diff(4),'rr':d.i-d.cpi})
show('saving',ols(d.sav,X,lambda p:p not in COV and p not in [pd.Period('2022Q1'),pd.Period('2022Q2')]))
json.dump(out,open('crisis_est.json','w'))
print(d[['gilt','debt','apf','mort','msp','sav']].tail(4).round(2))
