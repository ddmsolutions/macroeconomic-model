from bt2 import *
import json
e=pd.read_csv('data2/eri_q.csv',index_col=0); e.index=pd.PeriodIndex(e.index,freq='Q')
d=act.join(e); d['lerx']=np.log(d.eri)*100; d['dhe4']=d.lhe-L(d.lhe,4)
out={}
def pack(m): return {'coef':{k:round(float(v),5) for k,v in m.params.items()},'t':{k:round(float(v),2) for k,v in m.tvalues.items()},'r2':round(float(m.rsquared),3),'se':round(float(np.sqrt(m.scale)),3),'n':int(m.nobs)}
X=pd.DataFrame({'const':1.0,'w1':L(d.pay),'hi':np.maximum(0,L(d.cpi)-4),'ug1':L(d.u-d.ustar),'dinact':L(d.dinact)})
out['wage']=pack(ols(d.pay,X,EX))
X=pd.DataFrame({'const':1.0,'f1':L(d.food),'doil2':L(d.doil,2),'dhe1':L(d.dhe4),'dfx2':L(d.dfx,2),'w1':L(d.pay)})
out['food']=pack(ols(d.food,X,EX))
X=pd.DataFrame({'const':1.0,'s1':L(d.serv),'w1':L(d.pay),'cpi1':L(d.cpi)})
out['serv']=pack(ols(d.serv,X,EX))
Xp=pcX(d); Xp['wg1']=L(d.pay)-3.5
out['pcw']=pack(ols(d.dp-0.5,Xp,EX))
X=pd.DataFrame({'di':d.i.diff(),'le1':L(d['lerx'].diff())})
out['eri_i']=pack(ols(d['lerx'].diff(),X,EX))
h=d.loc['2024Q3':'2026Q2']
out['hist']={'q':[str(p) for p in h.index],'pay':h.pay.tolist(),'food':h.food.tolist(),'serv':h.serv.tolist(),'inact':h.inact.tolist(),'lts':h.lts.tolist(),'dhe4':h.dhe4.round(3).tolist(),'doil':h.doil.round(3).tolist(),'dfx':h.dfx.round(3).tolist(),'eri':h.eri.round(2).tolist()}
json.dump(out,open('est2_export.json','w'),indent=0)
for k,v in out.items():
    if k!='hist': print(k,v['coef'],v['t'],v['r2'])
print(out['hist'])
