# Is the CPI degradation from the extra 1989-92 history, or from small differences
# in the fetched series (FX convention, oil averaging)? Three configs, same origins.
import os, sys, time
import pandas as pd, numpy as np
rm=lambda x: float(np.sqrt((np.asarray(x)**2).mean()))
origins=[p for p in pd.period_range('2004Q4','2025Q2',freq='Q')
         if not (pd.Period('2019Q1')<=p<=pd.Period('2021Q4'))][::3]
def run(tag, env, trunc=None):
    for k in list(sys.modules):
        if k in ('m2',): del sys.modules[k]
    os.environ['UKMM_VINTAGE']=env
    import m2; raw=m2.RAW if trunc is None else m2.RAW.loc[trunc:]
    act=m2.prep(raw); act['gyy']=m2.gyy(act); rows=[]
    for T in origins:
        if T not in raw.index: continue
        d=m2.prep(raw.loc[:T]); mm=m2.fit(d); H=12
        e=m2.simulate(mm,d,H); e['gyy']=m2.gyy(e)
        for h in (4,8,12):
            tp=T+h
            if tp>raw.index[-1] or tp in m2.COV2: continue
            rows.append({'h':h,**{v:e.loc[tp,v]-act.loc[tp,v] for v in ['gyy','cpi','u','i']}})
    R=pd.DataFrame(rows)
    print('%-22s %s  n=%d' % (tag, m2.PANEL_SOURCE, len(R)))
    return R
res={}
res['static']        = run('static 1993+','static')
res['vintage 1989+'] = run('vintage 1989+','')
res['vintage 1993+'] = run('vintage, cut to 1993+','',trunc=pd.Period('1993Q1'))
print()
print('%-6s %-4s %10s %14s %14s'%('var','h','static','vintage 1989+','vintage 1993+'))
for v in ['gyy','cpi','u','i']:
    for h in (4,8,12):
        vals=[rm(res[k][res[k].h==h][v]) for k in ['static','vintage 1989+','vintage 1993+']]
        print('%-6s %-4d %10.3f %14.3f %14.3f'%(v,h,*vals))
