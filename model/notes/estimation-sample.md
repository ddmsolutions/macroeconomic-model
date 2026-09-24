# Why the estimation sample starts in 1993

Ingested vintages reach back to **1989Q1**; the model estimates from **1993Q1**. That is a
deliberate constraint, not a data limitation, and it was tested.

## The test

Three configurations over the same origins and horizons, differing only in data source and
sample start:

| | GDP h4 | GDP h12 | **CPI h8** | **CPI h12** | Unemp h4 | Rate h12 |
|---|---|---|---|---|---|---|
| static panel, 1993+ | 2.849 | 3.104 | **1.170** | **1.272** | 0.740 | 2.376 |
| vintage, 1993+ | 2.854 | 3.087 | **1.284** | **1.297** | 0.740 | 2.301 |
| vintage, 1989+ | 2.584 | 2.835 | **1.776** | **1.588** | 0.678 | 2.131 |

Two readings:

**The ingested data is equivalent to the static panel.** Cut to the same 1993 start, every
variable matches within noise. The remaining CPI gap of about 10% traces to the sterling
series, where the fetched quarterly average and the panel's own convention correlate 0.985.

**The extra history is the problem, and only for inflation.** Adding 1989-92 improves GDP by
roughly 9% and unemployment by 8%, and costs **38% on CPI at h=8** and 22% at h=12.

## Why

The UK adopted inflation targeting in **October 1992**. Before that there was no target,
sterling was in and then out of the ERM, and inflation ran from about 8% down to 2% through
a sterling crisis.

The Phillips curve in `m2.py` subtracts a fixed 0.5 quarterly anchor, which assumes a 2%
annual target. That assumption is simply false before 1993. Estimating across the break
blends two monetary regimes into one equation and the inflation forecasts pay for it.

GDP, unemployment and the policy rule are less sensitive, because output and labour-market
dynamics did not change regime in the same way. Hence the split result.

## What this means in practice

Use the vintage for the data and 1993Q1 for the sample. `SAMPLE_START` in `m2.py` defaults
to `1993Q1`; `UKMM_START` overrides it, and `UKMM_START=all` uses everything available.

The pre-1993 data is still worth having on disk. It would support a regime-switching
treatment, or an equation estimated with a time-varying anchor rather than a fixed one,
which is the honest way to use it.

## Reproducing

```bash
cd model
python vintage_diag.py      # the three-way comparison above
```
