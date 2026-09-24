from bt2 import *
e=pd.read_csv('data2/eri_q.csv',index_col=0); e.index=pd.PeriodIndex(e.index,freq='Q')
d=act.join(e); d['lerx']=np.log(d.eri)*100; d['qe']=d['lerx'].diff()
Xu=pcX(d)
Xe=pcX(d).drop(columns=['qfx1','qfx2','qfx3','qfx4'])
for k in (1,2,3,4): Xe[f'qe{k}']=L(d.qe,k)
for nm,X in (('usd',Xu),('eri',Xe)):
    m=ols(d.dp-0.5,X,EX); print(nm,'R2',round(m.rsquared,4),'SE',round(np.sqrt(m.scale),4))
    print(pd.DataFrame({'c':m.params.round(4),'t':m.tvalues.round(2)}).T.to_string())
    fxc=[c for c in m.params.index if c.startswith('qe') or c.startswith('qfx')]
    print(' sum fx lags',round(m.params[fxc].sum(),4),' joint se',round(np.sqrt(m.cov_params().loc[fxc,fxc].values.sum()),4))
# restricted: sum-of-lags single regressor
Xe2=pcX(d).drop(columns=['qfx1','qfx2','qfx3','qfx4']); Xe2['qe14']=sum(L(d.qe,k) for k in (1,2,3,4))
m=ols(d.dp-0.5,Xe2,EX); print('eri restricted',round(m.params['qe14'],4),'t',round(m.tvalues['qe14'],2),'R2',round(m.rsquared,4))
Xu2=pcX(d).drop(columns=['qfx1','qfx2','qfx3','qfx4']); Xu2['qf14']=sum(L(d.qfx,k) for k in (1,2,3,4))
m=ols(d.dp-0.5,Xu2,EX); print('usd restricted',round(m.params['qf14'],4),'t',round(m.tvalues['qf14'],2),'R2',round(m.rsquared,4))
# exports/imports not available; sterling vs rates using ERI
X=pd.DataFrame({'di':d.i.diff(),'le1':L(d['lerx'].diff())})
m=ols(d['lerx'].diff(),X,EX); print('eri on rate changes',m.params.round(3).to_dict(),m.tvalues.round(2).to_dict())
