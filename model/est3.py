from bt2 import *
d=act
for thr in (3,4,5):
    X=pd.DataFrame({'const':1.0,'w1':L(d.pay),'cpi1':L(d.cpi),'hi':np.maximum(0,L(d.cpi)-thr),'ug1':L(d.u-d.ustar),'dinact':L(d.dinact)})
    m=ols(d.pay,X,EX); print(thr,'R2',round(m.rsquared,3),'SE',round(np.sqrt(m.scale),3)); print(pd.DataFrame({'c':m.params.round(4),'t':m.tvalues.round(2)}).T.to_string())
# services with hi
X=pd.DataFrame({'const':1.0,'s1':L(d.serv),'w1':L(d.pay),'cpi1':L(d.cpi)})
m=ols(d.serv,X,EX); print('serv',pd.DataFrame({'c':m.params.round(4),'t':m.tvalues.round(2)}).T.to_string())
# pre-2020 only sample for wage eq, then does it forecast 2022?
X=pd.DataFrame({'const':1.0,'w1':L(d.pay),'cpi1':L(d.cpi),'hi':np.maximum(0,L(d.cpi)-4),'ug1':L(d.u-d.ustar)})
m=ols(d.pay,X,lambda p:p<pd.Period('2020Q1')); print('pre2020',m.params.round(3).to_dict())
