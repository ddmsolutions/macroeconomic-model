# Household energy: can wholesale gas replace the Ofgem cap assumption?

Short answer: no, and the premise was wrong to begin with.

## The premise was wrong

I had been calling the `+13% then +4%` energy path in `fc.py` the model's biggest
hand-typed assumption and the obvious thing to endogenise. It is not an assumption.
Ofgem announced the cap rising 13% from July 2026 and a further 4% from October 2026.
For 2026Q3 and 2026Q4 the model is using published fact, which is the best input that
exists. Replacing it with an equation would have swapped known data for a forecast.

What is genuinely a judgement call is only what happens after the announced window:
the model holds the cap flat from 2027Q1 onward. That, and only that, is what the
gas work was actually testing.

## The gas equation looks strong

`energy.py` regresses the household energy CPI year-on-year rate on European wholesale
gas growth at lags 1-2 plus its own lag, from 1997Q1:

    R2 0.811, se 7.57, n 118
    g2 0.0759 (t 4.09), h1 0.6320 (t 12.14)
    long-run pass-through 0.188

The lead structure is exactly what the institutional mechanism predicts. Univariate R2
on gas alone rises monotonically with the lag: 0.073 contemporaneous, then higher at
each lag out to 0.658 at four quarters. That is the cap transmission lag showing up in
the data, not a fluke of one specification.

## It still fails the full-model test

Feeding a forecast energy path into the four-equation system and backtesting CPI over
30 recursive origins (`energy_test.py`, `energy_test2.py`):

    variant         h=4      h=8     h=12
    flat          1.687    1.272    1.208
    lags12        1.734    1.569    1.289
    lags34        1.676    1.500    1.308
    pinned34      1.686    1.278    1.202

`lags12` and `lags34` are clearly worse at h=8, by 23% and 18%. `pinned34`, which
applies gas only for the quarters already determined by observed gas and holds flat
beyond, is a wash: better at h=4 and h=12, marginally worse at h=8, nothing that
survives rounding.

Two reasons it fails:

1. **The gas path has to be forecast too.** Beyond the determined window the projection
   extrapolates gas at its last observed growth rate and lets the autoregression run.
   Set `ENERGY='gas'` and CPI sits at 2.75 to 2.99 out to 2030, permanently above
   target, because the AR never lets energy inflation die. Holding energy flat is a
   better implicit forecast than any AR path the equation can produce.
2. **The coefficient is not stable.** Gas pass-through roughly doubled after 2022:
   0.026 estimated to 2010, 0.033 to 2021, 0.068 to 2023, 0.069 to 2026. Unlike the
   wage kink it never flips sign and R2 stays in 0.73-0.81 throughout, and the Ofgem
   cap moving to quarterly updates in late 2022 is a plausible mechanism. But an
   equation whose central parameter doubles mid-sample cannot be trusted 8 quarters out.

## What ships

`ENERGY` in `fc.py`, defaulted to `False`. The announced cap is preserved either way;
the flag only governs the tail. `'pinned'` and `'gas'` are wired and work, and are kept
so the question can be reopened against a gas futures curve, which carries genuine
forward information the naive extrapolation tested here does not.

This is the same result as the wage kink and one-sided filtering: a good in-sample fit
that does not survive contact with the full model. Third one today.

## Worth doing instead

Automate reading the announced cap rather than retyping it each quarter. Ofgem publishes
it, it is the single highest-value energy input, and it is currently a literal in
`fc.py`.
