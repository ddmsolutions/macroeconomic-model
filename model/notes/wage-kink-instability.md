# The wage-inflation coefficient is not identified outside 2022-23

`kink_stability.py` re-estimates the wage equation at every origin from 2008Q4 to 2026Q2
using only the data available at that point, and reports the inflation coefficient.

## Result

| Origin | `hi` (kinked) | t | `cpi1` (linear) | t | n |
|--------|--------------|---|----------------|---|---|
| 2011Q4 | -0.201 | -0.41 | -0.205 | -2.28 | 43 |
| 2015Q4 | -0.111 | -0.31 | -0.047 | -0.86 | 59 |
| 2019Q4 | -0.163 | -0.49 | -0.034 | -0.72 | 75 |
| **2021Q4** | **-0.155** | **-0.47** | -0.033 | -0.71 | 75 |
| **2022Q4** | **+0.178** | **+3.13** | +0.064 | +2.01 | 79 |
| 2024Q4 | +0.159 | +3.78 | +0.073 | +2.64 | 87 |
| 2026Q2 | +0.157 | +3.94 | +0.075 | +2.79 | 93 |

**Negative at all 53 origins from 2008Q4 to 2021Q4. Positive at all 18 origins from 2022Q1.**
The sign flips the quarter the 2022-23 surge enters the estimation sample.

## What this means

The full-sample coefficient of +0.157 at t=3.94 looks like strong evidence for a
wage-price channel. It is not. **Before 2022 the same specification gave a negative
coefficient that was never distinguishable from zero** (|t| < 0.5 throughout). All of the
statistical support comes from one episode, and the kink specification was chosen after
observing that episode.

Three consequences:

1. The t-statistic reflects one regime, not 93 quarters. It should not be read as a stable
   structural parameter.
2. At the origin where the channel was most needed, 2021Q4, the estimated coefficient said
   wage growth **falls** when inflation rises. Feeding the equation actual realised
   inflation from that origin drives predicted pay growth to **-0.3%** against an outturn of
   7.8%, worse than giving it no inflation signal at all.
3. The same pattern holds for the linear specification, so this is not an artefact of the
   kink. It is the underlying relationship that is unidentified.

## Recommendation

Do not switch `WAGE` on using an estimated inflation coefficient.

If the wage-price channel is wanted, **calibrate it rather than estimate it**, from external
evidence on pass-through, and treat it as a scenario lever rather than a fitted parameter.
The model already does exactly this for `RG` and `OILD` in `m2.py`, both calibrated with a
comment rather than estimated, so the convention exists.

That also makes the channel useful for the scenario lab, which is where a wage-price spiral
question actually belongs, without asserting that the data identifies its strength.

## Reproducing

```bash
cd model
python kink_stability.py    # writes kink_stability.csv
python kinktest.py          # kink on forecast vs anchored vs realised inflation
```
