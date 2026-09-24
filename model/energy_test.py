# Decisive test: in the full model, does forecasting household energy from gas beat
# the unconditional default of holding it flat? Recursive, same origins as eval3.
import sys; sys.path.insert(0,'data2')
import numpy as np, pandas as pd, m2, energy
rm=lambda x: float(np.sqrt((np.asarray(x)**2).mean()))
E=energy.load()
act=m2.prep(m2.RAW); act['gyy']=m2.gyy(act)
origins=[p for p in pd.period_range('2006Q4','2024Q2',freq='Q')
         if not (pd.Period('2019Q1')<=p<=pd.Period('2021Q4'))][::2]

def lhe_from_yoy(hist_lhe, yoy_path, idx):
    """Convert a y/y forecast into the log-level path simulate() expects."""
    lv = list(np.exp(np.asarray(hist_lhe)/100.0))     # back to levels
    out=[]
    for j,_ in enumerate(idx):
        base = lv[-4] if len(lv)>=4 else lv[-1]
        nxt = base*(1+float(yoy_path[j])/100.0)
        lv.append(nxt); out.append(np.log(nxt)*100.0)
    return np.array(out)

rows=[]
for T in origins:
    if T not in m2.RAW.index or T not in E.index: continue
    d=m2.prep(m2.RAW.loc[:T]); mm=m2.fit(d); H=12
    idx=pd.period_range(T+1,T+H,freq='Q')
    # gas-driven energy, estimated on data available at T only
    try:
        me=energy.fit(E, upto=T)
        yoy,det=energy.project(E.loc[:T], me, H)
        lhe=lhe_from_yoy(d.lhe.iloc[-8:].values, yoy.values, idx)
    except Exception:
        continue
    for tag,arg in [('flat',None),('gas',lhe)]:
        e=m2.simulate(mm,d,H,None,None,arg); e['gyy']=m2.gyy(e)
        for h in (4,8,12):
            tp=T+h
            if tp>m2.RAW.index[-1] or tp in m2.COV2: continue
            rows.append({'T':T,'h':h,'v':tag,**{k:e.loc[tp,k]-act.loc[tp,k] for k in ['cpi','gyy','i']}})
R=pd.DataFrame(rows)
print('origins used: %d\n'%R['T'].nunique())
print('%-6s %-4s %10s %10s %9s'%('var','h','energy flat','gas-driven','change'))
for v in ['cpi','gyy','i']:
    for h in (4,8,12):
        a=rm(R[(R.v=='flat')&(R.h==h)][v]); b=rm(R[(R.v=='gas')&(R.h==h)][v])
        print('%-6s %-4d %10.3f %10.3f %+8.1f%%'%(v,h,a,b,(b-a)/a*100))
    print()
