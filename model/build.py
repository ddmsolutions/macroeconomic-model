import pandas as pd, numpy as np, datetime as dt
from raw import *
def q(s):
    d={}
    for line in s.strip().splitlines():
        k,v=line.split(','); y,qq=k.split(); d[pd.Period(f"{y}{qq}",'Q')]=float(v)
    return pd.Series(d)
df=pd.DataFrame({'g':q(GDP),'cpi':q(CPI),'u':q(U)})
# Bank Rate quarterly average from daily step function
ch=[(dt.datetime.strptime(a,'%d %b %y'),float(b)) for a,b in (l.split(',') for l in BR.splitlines())]
days=pd.date_range('1993-01-01','2026-09-30')
r=pd.Series(np.nan,index=days)
for d_,v in ch:
    r[r.index>=d_]=v
df['i']=r.resample('QE').mean().to_period('Q').reindex(df.index)
b=pd.read_csv('brent.csv',parse_dates=['Date']).set_index('Date')['Price']
df['oil']=b.resample('QE').mean().to_period('Q').reindex(df.index)
fx=pd.read_csv('fx_monthly.csv',parse_dates=['Date']);fx=fx[fx.Country=='United Kingdom'].set_index('Date')['Exchange rate']
df['usdgbp']=(1/fx).resample('QE').mean().to_period('Q').reindex(df.index)
df.to_csv('uk_quarterly.csv')
print(df.tail(8)); print(df.describe().T[['count','min','max']])
# spot checks: annual growth
lvl=(1+df.g/100).cumprod()
ann=lvl.groupby(lvl.index.year).mean().pct_change()*100
print(ann.loc[[2008,2009,2019,2022,2023,2024,2025]].round(1))
