import pandas as pd, numpy as np, statsmodels.api as sm, sys
sys.path.insert(0,'data2')
from m2 import *
from series import load
d=prep(RAW)
s=load(); s.index=pd.PeriodIndex(s.index,freq='Q')
d=d.join(s)
d['dhe4']=d.lhe-L(d.lhe,4)
EX=lambda p: p not in COV
def rep(name,m):
    print('=====',name,'R2',round(m.rsquared,3),'SE',round(np.sqrt(m.scale),3),'n',int(m.nobs),m.model.data.row_labels[0],m.model.data.row_labels[-1])
    print(pd.DataFrame({'coef':m.params.round(4),'t':m.tvalues.round(2)}).T.to_string())
# wage equation (y/y regular pay, 3m avg)
X=pd.DataFrame({'const':1.0,'w1':L(d.pay),'cpi1':L(d.cpi),'ug1':L(d.u-d.ustar)})
mw=ols(d.pay,X,EX); rep('wage',mw)
X2=X.copy(); X2['cpi2']=L(d.cpi,2); X2['w2']=L(d.pay,2)
rep('wage2',ols(d.pay,X2,EX))
X3=X.copy(); X3['dinact']=L(d.inact-L(d.inact,4))
rep('wage3 inact',ols(d.pay,X3,EX))
# food
X=pd.DataFrame({'const':1.0,'f1':L(d.food),'doil2':L(d.doil,2),'dhe1':L(d.dhe4),'dfx2':L(d.dfx,2),'w1':L(d.pay)})
rep('food',ols(d.food,X,EX))
X=pd.DataFrame({'const':1.0,'f1':L(d.food),'doil2':L(d.doil,2),'doil4':L(d.doil,4),'dhe1':L(d.dhe4),'dfx2':L(d.dfx,2),'dfx4':L(d.dfx,4)})
rep('food nowage',ols(d.food,X,EX))
# services
X=pd.DataFrame({'const':1.0,'s1':L(d.serv),'w1':L(d.pay),'ug1':L(d.u-d.ustar)})
rep('serv',ols(d.serv,X,EX))
# augmented PC
Xp=pcX(d); Xp['wg1']=L(d.pay)-3.5
rep('pc+wage',ols(d.dp-0.5,Xp,EX))
Xp=pcX(d); Xp['ff1']=L(d.food-d.cpi)
rep('pc+food',ols(d.dp-0.5,Xp,EX))
Xp=pcX(d); Xp['wg1']=L(d.pay)-3.5; Xp['ff1']=L(d.food-d.cpi)
rep('pc+both',ols(d.dp-0.5,Xp,EX))
rep('pc base same sample',ols(d.dp-0.5,pcX(d),lambda p: EX(p) and p>=pd.Period('2001Q2')))
