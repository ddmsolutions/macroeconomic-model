import pandas as pd, numpy as np, json
from m2 import *
from bt2 import prepx, fitw, simw

# WAGE: endogenise pay and use the wage-augmented Phillips curve (pcw) instead of pc.
#   False  -> m2.simulate, the four-equation system. Reproduces the published baseline.
#   'hi'   -> bt2.simw with the kinked wage equation, wages respond to inflation above 4%.
#             Best CPI RMSE at h=8 (1.174 vs 1.208 base) and the only spec that beats a
#             naive pay forecast at any horizon (h=4, 1.066 vs 1.143).
#   True   -> bt2.simw with the linear wage equation. Dominated by 'hi'; kept for comparison.
# Caveat before switching: the kink conditions on the model's OWN inflation forecast, so it
# cannot rescue a bad inflation call. In the 2022 backtest it under-forecast pay worse than
# the linear spec. See output/2026-09-24_wage-equation-wiring.md.
WAGE = False

ev=json.load(open('eval_out.json'))
if WAGE:
    d=prepx(RAW); m=fitw(d)
    sim=lambda H,lo,lfx,lhe,addf,gaf: simw(m,d,H,lo,lfx,lhe,WAGE,addf,gaf)
else:
    d=prep(RAW); m=fit(d)
    sim=lambda H,lo,lfx,lhe,addf,gaf: simulate(m,d,H,lo,lfx,lhe,addf,gaf)
T=d.index[-1]; H=18; idx=pd.period_range(T+1,T+H,freq='Q')   # 2026Q3..2030Q4
oil=np.r_[91.0, np.full(H-1,100.0)]; lo=np.log(oil)*100
lfx=np.full(H,np.log(1.345)*100)
# Household energy. The first two quarters are NOT an assumption: Ofgem announced the cap
# rising 13% from July 2026 and a further 4% from October, so 2026Q3 and 2026Q4 are published
# fact. ENERGY controls only what happens AFTER the announced cap runs out.
#   False    -> hold the cap flat past the announced window. This is the default and it is
#               what the evidence supports (see notes/energy.md).
#   'gas'    -> extrapolate from European wholesale gas via energy.py. In sample the gas
#               equation is strong (R2 0.811, long-run pass-through 0.188, and R2 on the gas
#               lag rising monotonically to 0.658 at four quarters, which is cap transmission
#               showing up in the data). Out of sample it makes CPI WORSE: h=8 RMSE 1.569 vs
#               1.272 flat, because the gas path itself has to be forecast and the
#               pass-through coefficient roughly doubled after the cap went quarterly in 2022.
#   'pinned' -> apply gas only for the quarters already determined by observed gas, flat
#               beyond. A wash against flat (1.686/1.278/1.202 vs 1.687/1.272/1.208), so it
#               buys complexity and no accuracy. Kept because it is the only non-harmful
#               variant and it is the one to revisit against a gas futures curve.
ENERGY = False

_cap = [1.13, 1.13*1.04]
lhe = np.r_[[d.lhe.iloc[-1]+np.log(c)*100 for c in _cap],
            np.full(H-len(_cap), d.lhe.iloc[-1]+np.log(_cap[-1])*100)]
if ENERGY:
    import energy as _en
    _ed = _en.load(); _em = _en.fit(_ed)
    _yoy, _ndet = _en.project(_ed, _em, H)
    _n = len(_cap) + (_ndet if ENERGY == 'pinned' else H)
    for _q in range(len(_cap), min(_n, H)):
        lhe[_q] = lhe[_q-4] + _yoy[_q]       # year-on-year rate onto the level four back
    print('energy: %s, gas applied to quarters %d..%d of %d' % (ENERGY, len(_cap), min(_n,H)-1, H))
def run(af):
    return sim(H,lo,lfx,lhe,{idx[0]:af},None)

# Nowcast for the first forecast quarter. nowcast.py computes the monthly GDP
# carry-over and the quarterly CPI rate from published months; PMI is proprietary
# and cannot be fetched, so it is blended in here by hand when available.
# Set PMI_GROWTH=None to use the carry-over alone.
PMI_GROWTH = 0.3        # Sept 2026 flash composite PMI 51.7 implies about this
NOWCAST_OVERRIDE = None # set a number to bypass the computed nowcast entirely
try:
    import nowcast as _nc
    _n = _nc.nowcast(pmi_growth=PMI_GROWTH)
    NOWCAST  = _n['gdp']['growth'] if _n['gdp'] else 0.5
    CPI_TGT  = _n['cpi']['rate']   if _n['cpi'] else 3.1
    print('nowcast %s: GDP %+.2f%% (%d/3 months), CPI %.2f%% (%d/3 months)' % (
        _n['gdp']['quarter'], NOWCAST, _n['gdp']['months_published'], CPI_TGT, _n['cpi']['months_published']))
except Exception as _e:
    NOWCAST, CPI_TGT = 0.5, 3.1
    print('nowcast unavailable (%s), falling back to NOWCAST=%.2f CPI=%.2f' % (str(_e)[:60], NOWCAST, CPI_TGT))
if NOWCAST_OVERRIDE is not None: NOWCAST = NOWCAST_OVERRIDE
def run(af,gf=0.0):
    return sim(H,lo,lfx,lhe,{idx[0]:af},{idx[0]:gf})
lo_g,hi_g=-3,3
for _ in range(40):
    mg=(lo_g+hi_g)/2; g0=run(0.0,mg).g[idx[0]]
    if g0>NOWCAST: hi_g=mg
    else: lo_g=mg
gaf=mg
lo_af,hi_af=-2,2
for _ in range(40):
    mid=(lo_af+hi_af)/2; c=run(mid,gaf).cpi[idx[0]]
    if c>CPI_TGT: hi_af=mid
    else: lo_af=mid
af=mid; e=run(af,gaf); e['gyy']=gyy(e)
q=e.loc[idx,['g','gyy','cpi','u','i','gap','dp']].round(3); print(q)
full=e.loc[pd.period_range('2026Q1','2030Q4',freq='Q')]
yrs=[2026,2027,2028,2029,2030]
lvl=(1+e.g/100).cumprod()
ann_g=[float((lvl[e.index.year==y].mean()/lvl[e.index.year==y-1].mean()-1)*100) for y in yrs]
ann=lambda c: [float(e[c][e.index.year==y].mean()) for y in yrs]
end=lambda c: [float(e[c][pd.Period(f"{y}Q4")]) for y in yrs]
model={'gdp':ann_g,'cpi':ann('cpi'),'unemp':ann('u'),'rate':end('i')}
print('model annual',{k:[round(x,2) for x in v] for k,v in model.items()})
# naive: last observed
naive={'gdp':[1.2]*5,'cpi':[3.1]*5,'unemp':[4.9]*5,'rate':[3.75]*5}
W=ev['W']; wmap={'gdp':W['gyy'],'cpi':W['cpi'],'unemp':W['u'],'rate':W['i']}
stat={k:[wmap[k]*model[k][t]+(1-wmap[k])*naive[k][t] for t in range(5)] for k in model}
# rate anchor = market pricing (21 Sep 2026: ~65% chance of a November hike, about 4.2% by mid-2027; 2028-30 extrapolated as a gently falling curve)
MARKET_RATE=[3.95,4.15,3.95,3.85,3.80]
ext={'gdp':[1.2,1.1,1.6,1.6,1.5],'cpi':[3.1,3.4,2.1,2.0,2.0],'unemp':[4.9,5.1,4.9,4.6,4.4],'rate':MARKET_RATE}
# weight on external rises with horizon (our evaluation covers up to 3 years)
wext=[0.5,0.5,0.5,0.75,0.75]
central={k:[round(wext[t]*ext[k][t]+(1-wext[t])*stat[k][t],2) for t in range(5)] for k in model}
print('stat',{k:[round(x,2) for x in v] for k,v in stat.items()}); print('central',central)
# band sigma per year: combined RMSE at horizon of year midpoint (Q3 2026 origin -> h)
RM=ev['RM']
def sig(v,hs):
    arr=RM[v]; return float(np.mean([arr[min(h,20)-1] for h in hs]))
hs={2026:[1,2],2027:[3,4,5,6],2028:[7,8,9,10],2029:[11,12,13,14],2030:[15,16,17,18]}
growth=lambda: None
sigma={'gdp':[sig('gyy',hs[y])*(0.5 if y==2026 else 0.8) for y in yrs],   # annual-average growth errors smaller than y/y quarterly
       'cpi':[sig('cpi',hs[y]) for y in yrs],'unemp':[sig('u',hs[y]) for y in yrs],'rate':[sig('i',[hs[y][-1]]) for y in yrs]}
sigma={k:[round(x,2) for x in v] for k,v in sigma.items()}
print('sigma',sigma)
# state for JS: last 8 quarters of history
hcols=['gap','dp','lp','i','u','cpi','lo','lfx','lhe','g']+(['pay'] if WAGE else [])
hist=d.loc[d.index[-8]:,hcols].round(5)
state={'q':[str(p) for p in hist.index],**{c:hist[c].tolist() for c in hist},
 'rstar':float(d.rstar.iloc[-1]),'ustar':float(d.ustar.iloc[-1]),'gpot':float(d.gpot.iloc[-1]),
 'seas':{str(k):float(v) for k,v in (d.lp.diff()-d.dp).groupby(d.sq).mean().items()},'af':af,
 'path':{'q':[str(p) for p in idx],'lo':lo.round(4).tolist(),'lfx':lfx.round(4).tolist(),'lhe':np.array(lhe).round(4).tolist()},
 'ymeanG0':float(lvl[e.index.year==2025].mean()),'gaf':gaf,'nowcast':NOWCAST,'cpi_target':CPI_TGT,'wage':WAGE}
coef={k:{kk:round(float(vv),5) for kk,vv in m[k].params.items()} for k in m}
coef['RG']=RG; coef['OILD']=OILD
se={k:round(float(np.sqrt(m[k].scale)),3) for k in m}; r2={k:round(float(m[k].rsquared),3) for k in m}
tv={k:{kk:round(float(vv),2) for kk,vv in m[k].tvalues.items()} for k in m}
out={'coef':coef,'se':se,'r2':r2,'t':tv,'state':state,'model_annual':model,'stat':stat,'ext':ext,'central':central,'sigma':sigma,'W':W,'wext':wext,
     'RM':{k:RM[k] for k in ['gyy','gyy_naive','cpi','cpi_naive','cpi_model','u','u_model','i','i_model','i_naive']},'CALM':ev['CALM'],'bt':ev['bt'],'nobs':{k:int(m[k].nobs) for k in m},
     'base_q':{c:[round(float(x),4) for x in e.loc[idx,c]] for c in ['g','cpi','u','i','gap']+(['pay'] if WAGE else [])}}
json.dump(out,open('model_export.json','w'))
print(json.dumps(coef))
