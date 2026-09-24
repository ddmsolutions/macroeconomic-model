# UK Macro Model

A quarterly macroeconomic model of the UK economy, with an interactive dashboard
projecting to 2030 and a scenario lab for testing shocks against a central path.

The dashboard is a single static page. The estimation code is Python and is not needed
to view it.

## What it does

- **Where the economy stands** - current read across growth, inflation, unemployment and rates
- **Outlook to 2030** - a central path, with RPI modelled on its own basket rather than derived
- **Scenario lab** - presets applied alone and combined, shown as deviation from baseline,
  with uncertainty bands and the automatic policy responses each scenario triggers
- **Fiscal rules** - where the scenario lands against the rules in 2029-30
- **Business lens** - sector exposure 2027-28, and borrowing costs
- **Households** - extra cost-of-living inflation versus the central path, and the spending
  shares behind it

## Running the dashboard

No build step. Open `index.html` in a browser, or serve the folder:

```bash
python -m http.server 8000
```

Chart.js is loaded from a CDN and fonts from Google Fonts, so the page needs internet access.

### Deploying

Vercel, framework preset "Other", no build command, output directory `.` (root).
`vercel.json` sets clean URLs and `X-Content-Type-Options: nosniff`.

## The model

Python, in `model/`. Single-equation estimation with `statsmodels`, exported to JSON that
the dashboard reads.

```bash
cd model
pip install -r requirements.txt
```

### Pipeline order

The scripts share state through JSON files and expect to be run from inside `model/`:

| Step | Script | Produces |
|------|--------|----------|
| 1 | `build.py` | assembles the quarterly panel from raw series |
| 2 | `est_final.py`, `est2.py`, `est3.py`, `est4.py` | equation estimates (`est2_export.json`, `model_export.json`) |
| 3 | `links.py` | cross-equation links (`links_est.json`) |
| 4 | `crisis_est.py` | crisis and balance-sheet terms (`crisis_est.json`) |
| 5 | `rpi.py` | RPI basket build-up (`rpi_export.json`) |
| 6 | `post.py` | backtest and evaluation output (`eval_out.json`) |
| 7 | `fc.py` | the forward path to 2030Q4 |

`model/eval_out.json` is a generated intermediate and is gitignored. `fc.py` will fail
until `post.py` has been run.

### Structure

```
model/
├── raw.py, build.py        # raw series and panel assembly
├── m2.py, bt2.py           # shared model definition and backtest helpers
├── est*.py, est_final.py   # equation estimation
├── links.py, crisis_est.py # cross-equation and crisis linkages
├── rpi.py, rpi_raw.py      # RPI on its own basket
├── eri.py, bands.py        # exchange rate index, uncertainty bands
├── post.py, eval3.py       # evaluation and backtesting
├── fc.py                   # forecast
└── data2/                  # secondary series and long-run facts
```

## Data

Quarterly UK macro series, 10-year gilt yields, Brent crude, sterling exchange rates and
an effective rate index, from 1971 onward depending on the series.

> **Note on provenance.** The CSVs do not currently carry source attribution. They are
> understood to come from public sources (ONS, Bank of England, EIA/FRED) published under
> open terms, but this has not been documented series by series. If you intend to rely on
> or redistribute the data, verify the original source first.

## Status

Personal research project. The estimates are the author's own and are not investment,
financial or policy advice.

## Licence

MIT. See [LICENSE](LICENSE). The licence covers the code; see the note above regarding data.
