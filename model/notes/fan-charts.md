# Why the fan charts stay empirical

The brief was to swap `bands.py` for `stoch.py` and delete the hand-set scale factors. The
factors are gone. The swap was not made, and the comparison is why.

## What the stochastic bands look like next to the empirical ones

Deviations from the central path, p05 to p95:

| | empirical | stochastic |
|---|---|---|
| GDP 2027 | -2.37 .. **+5.38** | -1.64 .. **+1.69** |
| GDP 2029 | -3.88 .. +5.00 | -2.60 .. +2.70 |
| Bank Rate 2027 | -2.46 .. **+4.21** | -1.19 .. **+1.20** |
| Unemployment 2028 | -2.36 .. +2.10 | -1.16 .. +1.25 |
| CPI 2027 | -2.29 .. +1.66 | -1.56 .. +1.58 |

The stochastic bands are roughly **half the width** on GDP and Bank Rate, and close to
symmetric where the empirical ones are strongly right-skewed.

## Why, and why it matters

`stoch.py` draws Gaussian shocks from the estimated residual covariance. That is shock
uncertainty and nothing else. The empirical errors are realised out-of-sample forecast
errors, so they also contain parameter uncertainty, specification error, and the regime
breaks of 2008-09 and 2021-23. Those are what produce the fat right tail on growth and
rates, and a Gaussian draw cannot reproduce them.

Adopting the simulated fan would therefore make the dashboard **look more confident than
the model's own track record justifies**, on a page whose distinguishing feature is that it
publishes that track record honestly. That is a bad trade.

## The factors are gone anyway, because they were arithmetic

The old file took quantiles of quarterly errors and averaged them across the horizons
falling in each year, then multiplied by hand:

    scale = {'gyy': {2026: 0.35}, 'cpi': {2026: 0.3}, 'u': {2026: 0.5}}
    f = scale[v].get(y, 1.0) * (0.8 if v == 'gyy' and y > 2026 else 1.0)

Averaging quantiles is not the quantile of the average, and a part-forecast year was not
represented. Both are fixed by computing each origin's annual error first, as the **sum of
that year's forecast-quarter errors divided by four**, and taking quantiles across origins
afterwards. 2026 comes out narrow on its own because only two of its quarters are forecast.

Checked against the old factors: they landed within about 25% of the correct answer for
2026-2028, so they were a crude version of the right calculation rather than an arbitrary
fudge. They broke down for 2029-2030 only because `err3.pkl` stopped at h=12 and the code
repeated the last horizon.

`eval3.py` now runs to **h=20**, so every year through 2030 is built from its own four
quarters. 2030 uses 44 origins.

## What stoch.py is still for

It stays, because it does something the empirical approach cannot: joint, probabilistic
statements from a coherent set of draws.

    P(CPI > 3% in 2027Q4)                    25%
    P(Bank Rate > 4% in 2027Q4)              33%
    P(both together)                         15%

Those need the same draws across variables, which a table of marginal error quantiles does
not provide. Use `stoch.py --bands` if a model-generated fan is ever wanted for comparison;
just do not publish it as the uncertainty measure.
