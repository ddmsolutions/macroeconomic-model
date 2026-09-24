# Commodities beyond crude: what earns a place

Four candidates tested against a random walk on the same sample (1997Q1 on, n≈118).
`python commodities.py` reproduces all of it.

## Petrol: yes, clearly

CPI motor fuels (07.2.2) against Brent expressed in sterling:

| specification | R2 | se | random walk |
|---|---|---|---|
| sterling crude, contemporaneous | 0.684 | 6.09 | 7.06 |
| plus one lag | 0.700 | 5.97 | 7.06 |
| **plus own lag** | **0.874** | **3.88** | 7.06 |

**Beats a random walk by 45%.** Unsurprising, because the pump price is close to an
identity: crude in sterling, plus duty, plus VAT. It is worth having precisely because it
is mechanical, and because motor fuels were the main driver of the August 2026 CPI rise.

## Gas: yes, and it fixes the model's biggest assumption

European wholesale gas against UK household energy CPI, at increasing lags:

| gas lagged | R2 |
|---|---|
| 0 quarters | 0.073 |
| 1 | 0.256 |
| 2 | 0.506 |
| 3 | 0.626 |
| **4** | **0.658** |

The relationship strengthens monotonically out to a year. **That is the Ofgem cap
transmission visible in the data**: wholesale prices enter the cap through a defined
observation window and reach household bills with a long, fairly mechanical lag.

Gas alone loses to a random walk at every single lag. Combined with the series' own lag it
wins: R2 0.811, se 7.57 against 9.84.

The consequence matters more than the fit. `fc.py` currently **assumes** household energy at
+13% then +4%, hand-typed. Energy was the single largest inflation driver of 2022. A
relationship this strong at a three to four quarter lead means household energy is
forecastable roughly a year ahead from an observable wholesale price. That converts the
biggest remaining assumption in the model into a forecast.

It also improves headline CPI directly:

| CPI forecast | R2 | se |
|---|---|---|
| own lags only | 0.921 | 0.56 |
| **plus lagged European gas** | **0.937** | **0.50** |

An 11% reduction in standard error on the variable the model exists to forecast.

## Gold: no

| specification | R2 | se | random walk |
|---|---|---|---|
| on lagged UK real rate | **0.015** | 17.66 | 9.25 |
| real rate, CPI, sterling | 0.097 | 17.06 | 9.25 |
| plus own lag | 0.744 | 9.03 | 9.25 |

The UK real rate explains **1.5%** of gold's variance. The only specification that beats a
random walk does so through gold's own lag, which is overlapping-window persistence rather
than anything the model knows.

And it does not help in reverse: adding lagged gold to a CPI equation moves the standard
error from 0.56 to 0.56.

This is the expected answer. Gold is a dollar asset priced off global real yields and
central bank demand. A UK quarterly macro model has no information about it, and pretending
otherwise would repeat the wage-equation mistake of fitting a relationship the data does not
support.

## Silver: no, emphatically

| specification | R2 | se | random walk |
|---|---|---|---|
| on lagged UK real rate | **0.000** | 30.19 | 19.30 |
| plus UK GDP growth | 0.003 | 30.28 | 19.30 |
| plus lagged gold | 0.464 | 22.19 | 19.30 |

R2 of **zero** against the UK real rate, and 0.003 once GDP growth is added, so the
industrial-demand story does not show up either. Even with gold alongside it still loses to
a random walk.

## What was built

Petrol and gas earn equations. Gold and silver do not.

All four are ingested anyway (LBMA gold and silver fixes back to 1968, European gas from
FRED, CPI electricity, gas and motor fuels from ONS) because having the series costs
nothing and they are useful for display, for scenario work and outside this model. What
they have not earned is a place in the forecast.
