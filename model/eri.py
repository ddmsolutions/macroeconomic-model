import pandas as pd, numpy as np
fx=pd.read_csv('fx_monthly.csv'); fx['Date']=pd.to_datetime(fx.Date)
p=fx.pivot_table(index='Date',columns='Country',values='Exchange rate')
eur=p['Euro'].copy(); eur=eur.fillna(p['Germany']/1.95583)   # pre-1999 synthetic euro from DEM
usd_per_gbp=1/p['United Kingdom']
# foreign currency per GBP = (foreign per USD) * (USD per GBP)
W={'eur':0.48,'usd':0.21,'China':0.07,'Japan':0.03,'Switzerland':0.03,'Sweden':0.02,'Norway':0.02,'Canada':0.02,'India':0.02,'South Korea':0.01,'Australia':0.01}
cols={'eur':eur*usd_per_gbp,'usd':usd_per_gbp}
for k in W:
    if k not in cols: cols[k]=p[k]*usd_per_gbp
C=pd.DataFrame(cols).loc['1990':]
C=C.dropna(axis=0,how='any')
w=pd.Series(W)/sum(W.values())
lg=np.log(C).mul(w,axis=1).sum(axis=1)
eri=np.exp(lg-lg.loc['2005-01-01':'2005-12-01'].mean())*100
q=eri.resample('QS').mean(); q.index=q.index.to_period('Q')
q.to_csv('data2/eri_q.csv',header=['eri'])
print(q.loc['2007Q2':'2009Q2'].round(1).tolist()); print(q.loc['2016Q1':'2017Q1'].round(1).tolist()); print(q.tail(6).round(1).tolist(), C.index[-1])
