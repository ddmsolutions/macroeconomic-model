# Distributional and long-run facts for the UK macro model

Compiled 24 September 2026 using WebSearch and WebFetch only. Most figures were read through a page summariser, and many were checked against verbatim quotes. Tags:
- **[V]**: verified. The figure appears in the source page text, quoted directly or summarised from it.
- **[V-para]**: taken from a summary of the source that was not re-checked word for word. Treat as likely correct.
- **[UNVERIFIED]** / **[NOT FOUND]**: flagged as such. No figures are guessed.

Limitation: the ONS .xlsx workbooks returned HTTP 400 through WebFetch. This affects Family Spending workbook 2 and the population projection tables. Because of this, **full quintile-by-quintile category shares and decile rows could not be pulled.** Only the extreme quintiles published in bulletin text are given below. To fill the grid, download
https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/datasets/familyspendingworkbook2expenditurebyincome/fye2025/workbook2expenditurebyincome.xlsx
(Family spending workbook 2, FYE 2025. It has tables by disposable income decile and quintile, plus percentage-of-expenditure versions.)

---

## A. Household spending by income group

### A1. Weekly expenditure by quintile. ONS Family Spending FYE 2025 (Apr 2024 to Mar 2025), released 11 Jun 2026
Source: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2024tomarch2025

| Item | Value | Tag |
|---|---|---|
| Average weekly household expenditure, all households | £676.60 (nominal +£53.30 / +9% y/y; real +£35.10 / +5%) | V |
| Richest fifth weekly expenditure | £1,083.60 | V |
| Poorest fifth weekly expenditure | £407.30 | V |
| Ratio, richest to poorest | 2.7x (up from 2.5x in FYE 2024) | V (quoted) |
| Housing (net), fuel and power, all households | £118.40/wk = 18% of total | V-para |
| Transport, all households | £96.40/wk = 14% of total | V-para |
| Poorest fifth, real change in electricity, gas and other fuels spend | +£4.20 (+15%) | V (quoted) |
| Poorest fifth, net rent, nominal change | +£8.60 (+18%) | V (quoted) |
| Richest fifth, mortgage interest, nominal change vs FYE 2023 | +£18.30 (+34%) | V (quoted) |
| Middle quintiles (Q2 to Q4) | NOT FOUND in bulletin text (workbook only) | NOT FOUND |

Bulletin Figure 5 title: "Poorer households spent proportionally more on housing (net), fuel and power than richer households in FYE 2025." The values in the figure were not extractable.

### A2. Spending shares, poorest and richest fifth. ONS Family Spending FYE 2024 (Apr 2023 to Mar 2024)
Source: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/expenditure/bulletins/familyspendingintheuk/april2023tomarch2024

| Share of total expenditure | Poorest fifth | Richest fifth | Tag |
|---|---|---|---|
| Weekly expenditure (FYE 2024) | £378.60 | £948.70 | V |
| Housing (net), fuel and power | 27% | n/a in text | V (quoted) |
| Net rent | 13% | n/a | V (quoted) |
| Mortgage interest payments (ONS files these under "other expenditure") | n/a | 7% | V (quoted) |
| "Energy and fuel" | 10% | 5% | V (quoted: "The poorest fifth consistently spent double the proportion of total expenditure on energy and fuel since FYE 2022, spending 10% in FYE 2024 ... while the richest fifth spent 5%.") **Caveat: it is unclear whether "energy and fuel" means household energy only (electricity, gas and other fuels) or also includes motor fuel. Probably household energy only (inferred).** |

### A3. Food share by income. Defra Family Food FYE 2025
Source: https://www.gov.uk/government/statistics/family-food-fye-2025/family-food-fye-2025
- Lowest 20% income households: 15.2% of expenditure on household food and non-alcoholic drink [V]
- All households: 10.9% [V]
- Highest quintile: NOT FOUND in text.
- Note: this covers household food only (eating out excluded), so it is not exactly the ONS COICOP 01 share.

### A4. Items not found (need the workbook)
Motor fuel share by quintile, rent and mortgage shares for Q2 to Q4, the "everything else" residual, tenure mix by quintile (renters, mortgagors, outright owners): **NOT FOUND** in the web text. All are in Family spending workbook 2 (quintile table and tenure tables).

### A5. Disposable income by quintile. ONS Effects of taxes and benefits (ETB), FYE 2024, released 25 Sep 2025
Source: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/theeffectsoftaxesandbenefitsonhouseholdincome/2024
- Mean equivalised disposable income: poorest fifth £15,200/yr; richest fifth £85,600/yr [V-para]
- Mean original income: poorest fifth £9,600; richest fifth £116,600 [V-para]
- Richest-to-poorest ratio: 12.2x on original income, 3.3x on final income [V-para]
- Gini: original income 47.6%, final income 26.8% [V-para]
- Middle quintiles: NOT FOUND in text. I did not check whether an FYE 2025 ETB edition has been published.
- Note: these are equivalised annual incomes. Family Spending quintiles are ranked on household disposable income, so the two sources are not directly comparable.

### A6. Household Costs Indices (HCI) by income decile and tenure
ONS does not publish deciles 1 and 10: "The first- and tenth-income deciles are not included ... composition of these groups can be unusual". Deciles 2 and 9 are its proxies for low and high income.

**Latest: April to June 2026 bulletin, released 28 Aug 2026**
Source: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/householdcostsindicesforukhouseholdgroups/latest

| Group (annual rate, June 2026) | Rate | Tag |
|---|---|---|
| All households | 2.8% | V (quoted) |
| Decile 2 (low income) | 2.7% | V-para |
| Decile 9 (high income) | 2.8% | V-para |
| Other deciles | 2.7% to 2.9% | V-para |
| Private renters | 3.0% (highest) | V (quoted) |
| Mortgagors | 2.8% | V-para |
| Social/other renters | 2.7% | V-para |
| Outright owners | 2.6% (lowest) | V (quoted) |
| Non-retired / retired | 2.9% / 2.5% | V-para |

**January to March 2026 bulletin, released 28 May 2026**
Source: https://www.ons.gov.uk/economy/inflationandpriceindices/bulletins/householdcostsindicesforukhouseholdgroups/januarytomarch2026

| Annual rate | Jan 2026 | Feb 2026 | Mar 2026 | Mar 2025 |
|---|---|---|---|---|
| All households | | | 3.6% | 2.7% |
| Decile 2 | 3.3% | 3.3% | 3.7% | 2.6% |
| Decile 9 | 3.2% | 3.2% | 3.5% | 2.8% |
| Deciles 3 to 8 (Mar 2026) | 3.6 to 3.7% | | | |
| Private renters / social renters / mortgagors / outright owners (Mar 2026) | 3.7 / 3.7 / 3.6 / 3.6% | | | |
| Dec 2025, all households | 3.6% | | | |
Tag: V-para. CPI for Mar 2026 was 3.3% versus HCI 3.6%.
Drivers, Dec 2025 to Mar 2026: the motor fuels contribution rose from 0.02 to 0.14pp, electricity, gas and other fuels rose from 0.10 to 0.20pp, and food and non-alcoholic beverages fell by 0.11pp [V-para].

**Takeaway:** in 2025 to 2026 the low-to-high income gap in HCI inflation is small, at about ±0.2pp. Tenure matters more: private renters are highest and outright owners lowest.

---

## B. Tenure. English Housing Survey 2024-25 headline report (England)
Sources: https://assets.publishing.service.gov.uk/media/6930595d4bedc0e762303ffa/2024-25_EHS_Headline_Report.pdf ; https://www.gov.uk/government/statistics/chapters-for-english-housing-survey-2024-to-2025-headline-findings-on-demographics-and-household-resilience/introduction-and-key-findings

| Tenure | Share of households | Number | Tag |
|---|---|---|---|
| Owner occupiers | 65% | 16.2m | V (quoted) |
| Outright owners | 36% | 9.0m | V |
| Mortgagors | 29% | 7.2m | V |
| Private renters | 19% | 4.7m | V |
| Social renters | 16% | 4.1m | V |

| Housing cost burden (mean share of household income) | Incl. housing support | Excl. housing support | Tag |
|---|---|---|---|
| Mortgagors (mortgage payments) | 19% | n/a | V-para (quoted) |
| Private renters | 34% | 39% | V-para |
| Social renters | 28% | 39% | V-para |

Mean weekly costs in England: mortgage £242, private rent £250, social rent £129 [V-para]. London figures: mortgage £375, private rent £393, social rent £171. Rest of England: £220, £207, £119 [V].

---

## C. Long-run supply side

### C1. Population. ONS national population projections, 2024-based (the latest, released 28 Apr 2026; this replaces the 2022-based projections)
Sources: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/bulletins/nationalpopulationprojections/latest ; PDF: .../2024based/pdf

| Mid-year | UK total population | Tag |
|---|---|---|
| 2024 (base) | 69,281k | V |
| 2029 | 70,224k | V |
| 2034 | 71,014k | V |
| 2039 | 71,594k | V |
| 2044 | 72,063k | V |
| 2049 | 72,410k | V |

- Working age (defined by State Pension age): 44.3m (2024) rising to 45.8m (2034) [V-para]
- Pensionable age: 12.4m rising to 14.2m, +1.8m (+14.6%) from 2024 to 2034 [V]
- Children 0 to 15: 11.0m in 2034 (−1.6m) [V-para]. Aged 85+: 3.6m in 2049 [V-para]
- **Long-term net migration assumption: 230,000 a year from mid-2027** [V]. The OBR uses 230k in FRS 2026; its March 2026 EFO used 235k.
- TFR 1.42. Period life expectancy in 2049: female 85.9, male 82.4. Natural change 2024 to 2034: about −450,000 [V-para]
- **16-64 and 65+ for 2026, 2030, 2035, 2040: NOT FOUND** in bulletin text. They are only in the xlsx tables, which could not be fetched. The bulletin uses SPA-based working age, not 16-64.
- OBR FRS 2026 context: population about 70m in 2025, peaking just under 73m in the mid-2050s and about 71.5m by 2075. Old-age dependency ratio (65+/working age) about 30% in 2025 and over 40% by 2075 [V-para].

### C2. OBR productivity and potential output
**Medium term: OBR Briefing paper No. 9, Forecasting productivity (Nov 2025)**, https://obr.uk/docs/dlm_uploads/Briefing_paper_No.9_Forecasting_productivity.pdf
- Medium-term trend productivity growth: 1.0% a year (down from 1.3% in March 2025) [V-para]
- Split: TFP 0.8pp (was 1.1) plus capital deepening 0.2pp [V-para]. Labour quality is folded into TFP.
- "assumed capital share of income of one-third" [V (quoted)], so the implied labour share is 2/3.
- Potential labour supply growth 0.5% a year, giving medium-term potential output growth of 1.5% [V-para]

**EFO March 2026 (3 Mar 2026)**, https://obr.uk/efo/economic-and-fiscal-outlook-march-2026/
- Central medium-term productivity growth 1.0% a year [V-para]
- Potential output growth averages about 1.3% over 2026 to 2030, rising to 1.5% by 2030 [V-para]
- Output gap −0.8% in Q3 2025, closing by mid-2029 [V-para]
- Net migration assumption 235,000 a year. Trend participation 63.5% (2025) to 63.3% (2030). Adult population 56.7m (2025) to 58.1m (2030) [V-para]
- A summary said capital deepening "≈0.3pp". This conflicts with the 0.2pp in the briefing paper, so it is **[UNVERIFIED]**. Use 0.2pp.
- Business investment: "falls as a share of GDP from 11 per cent in 2025 to 10½ per cent in 2030" [V-para, from EFO PDF https://assets.publishing.service.gov.uk/media/69a6d7b62e1f4fbda4252208/economic-and-fiscal-outlook-march-2026-web-accessible.pdf]

**Long run: OBR Fiscal risks and sustainability, July 2026 (7 Jul 2026)**, https://obr.uk/frs/fiscal-risks-and-sustainability-july-2026/ ; PDF https://assets.publishing.service.gov.uk/media/6a4cb4c74889d85e75ab40e0/E03599617_OBR_FRS_2026_Accessible.pdf
- Long-term productivity growth "1.4 per cent over the next 50 years" [V]. It converges from the medium-term forecast (0.9% cited from the March 2026 EFO; this 0.9 vs 1.0 difference is unresolved).
- Real GDP growth about 1½% a year over the long term. Real GDP per person about 1½%. Nominal GDP 3.7% [V-para]
- Participation about 64%, broadly stable for about 30 years, then falling to about 61% by 2075. Employment rate about 61%, falling to just over 58% by 2075 [V-para]
- FRS 2026 decomposes trend productivity into capital deepening (capital per hour), TFP and labour quality for the first time. **The pp figures could not be extracted [NOT FOUND].** A higher-productivity scenario assumes TFP of 1.3% a year.

### C3. Capital, labour share, investment
- Labour share, ONS preferred measure (Method 5, adjusted for self-employment), 2023: about 59.5% of income. Unadjusted: about 53% [V-para]. https://www.ons.gov.uk/economy/economicoutputandproductivity/output/articles/trendsintheuklabourshare1997to2023/2024-11-25
- OBR assumes a capital share of 1/3 [V] (see C2)
- Net capital stock in 2024: £5.6 trillion (CVM), growth +1.4% (2023: +1.8%). Dwellings are 43.9% (£2.5tn). General government net stock grew 3.4% [V-para]. ONS Capital stocks and fixed capital consumption 2025 (27 Nov 2025): https://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts/bulletins/capitalstocksconsumptionoffixedcapital/2025
- Depreciation / CFC rate: **NOT FOUND** in the bulletin text. It is in dataset https://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts/datasets/capitalstock. Capital-output ratio: **NOT FOUND**. Inferred (not verified): £5.6tn net stock against about £2.9 to 3.0tn nominal GDP suggests a K/Y of about 2 (CVM vs nominal mix, rough).
- Business investment about 11% of GDP in 2025 (OBR, see C2)
- Public sector net investment FYE Mar 2026: £81.2bn [V-para]. About 2.6% of GDP [UNVERIFIED: the summariser inferred this from the PSA3 table]. PSNB £132.0bn = 4.3% of GDP [V (quoted)]. https://www.ons.gov.uk/economy/governmentpublicsectorandtaxes/publicsectorfinance/bulletins/publicsectorfinances/march2026/pdf

### C4. Ageing and public spending. OBR FRS July 2026 baseline (% of GDP)
| | 2030-31 | 2075-76 | Tag |
|---|---|---|---|
| Health | 8% | 13% (alternative scenario about 9%) | V (quoted) |
| State pension | 5% | about 9% with triple lock; about 7% if earnings-uprated | V (quoted) |
| Adult social care | 1.2% | 1.8% | V-para |
| Education | 4.3% | 3.4% | V-para |
| Total primary spending | 40% | 49% | V-para |
| Other welfare | about 6%, stable | | V-para |
- PSND starts rising from 2032-33 and is on a "clearly unsustainable upward trajectory by the late 2040s" [V]. Holding debt at 95% of GDP needs the primary deficit to be 3.8% of GDP lower from 2031-32 [V-para].
- **2040 and 2050 values: NOT FOUND in text.** They are in the FRS 2026 chart/data supplement. FRS July 2025 (8 Jul 2025) had state pension at about 5% of GDP (£138bn) in 2024-25 and 7.7% by the early 2070s: https://obr.uk/frs/fiscal-risks-and-sustainability-july-2025/

---

## D. Long-term sickness inactivity and welfare reform

- Inactive due to long-term sickness, aged 16-64 (LFS series LF69): **2,780k**, latest period in the release of 15 Sep 2026 [V-para]. The period label is ambiguous and reads as "June 2026"; it is probably the three-month rolling period May to July 2026 or Apr to Jun 2026. Recent quarters: Q3 2025 2,826k; Q4 2025 2,786k; Q1 2026 2,772k; Q2 2026 2,774k. 2019 was about 2,046k. https://www.ons.gov.uk/employmentandlabourmarket/peoplenotinwork/economicinactivity/timeseries/lf69/lms
- Total inactivity, Jan to Mar 2026: 9.1m, rate 20.9% (16-64). NEET 16-24: 1,012k (13.5%) [V-para, House of Lords Library]. https://lordslibrary.parliament.uk/welfare-reforms-and-youth-unemployment/

**Fiscal cost per person. OBR FRS July 2023** (the latest explicit per-person estimate found), https://obr.uk/frs/fiscal-risks-and-sustainability-july-2023/
- "average increase in universal credit awards of around £10,000 a year for this group" [V (quoted)]
- "average income tax and NICs loss ... around £5,000 a year for each person" [V (quoted)]
- Extra NHS cost of about £900 to £1,800 per person a year [V-para]
- Aggregate: the post-pandemic rise in inactivity (+440k) plus ill-health in work "added £6.8 billion to the annual welfare bill, cost £8.9 billion in foregone tax receipts ... added £15.7 billion (0.6 per cent of GDP) to annual borrowing" (2023-24) [V (quoted)]
- Scenario: "borrowing rises by £21.3 billion (0.8 per cent of GDP) by 2027-28" relative to central [V (quoted)]. **Scenario context not verified. Probably the OBR's higher-inactivity scenario (inferred).**
- Implied fiscal cost per additional inactive person: about £15,000/yr (£10k benefits plus £5k tax), excluding NHS costs. **Inferred** by summing the two OBR figures.

**Welfare reforms and employment effects**
- OBR EFO March 2025, Box 3.2: reversing the Nov 2023 WCA changes "reduces employment by 16,000 (and labour supply by 8,000 in average-hours-equivalent terms) in 2029-30". £1bn of employment support by 2029-30. The Pathways to Work Green Paper measures were not scored because they lacked detail [V (quoted)]. https://obr.uk/box/the-potential-impacts-of-welfare-reforms-that-have-not-been-incorporated-into-this-forecast/
- DWP impacts document, Spring Statement 2025: welfare savings of £4.8bn by 2029-30 (£4.5bn of it from working-age sickness and disability benefits). 3.2m families lose an average £1,720/yr and 3.8m families gain an average £420/yr. It said "The OBR will assess the labour supply impacts ... in their autumn forecast". **The DWP gave no employment estimate** [V-para]. https://assets.publishing.service.gov.uk/media/67e667fe4a226ab6c41b1fe2/spring-statement-2025-health-and-disability-benefit-reforms-impacts.pdf
- OBR EFO November 2025: **no quantified employment effect** of welfare reforms found. Personal tax measures were judged below the 0.1%-of-potential-output significance threshold. Removing the two-child limit costs £3bn by 2029-30 and benefits 560k families by an average £5,310 [V-para]. https://obr.uk/docs/dlm_uploads/OBR_Economic_and_fiscal_outlook_November_2025.pdf
- OBR EFO March 2026: incapacity benefit caseload growth of about 3% a year over the next three years, slowing to 1.3% in 2030-31 [V (quoted)].
- DWP press release, 18 Dec 2025 (updated 11 Sep 2026): reforms save £1.9bn by end-2030/31. Face-to-face assessments rise (PIP 6% to 30%, WCA 12% to 30%). Connect to Work to help 300,000 sick or disabled people into work by end of parliament. **This is a programme target, not an OBR-certified employment effect** [V-para]. https://www.gov.uk/government/news/reforms-to-welfare-system-set-to-save-19-billion-by-the-end-of-203031
- DWP, 6 Apr 2026: the UC health element for new claimants falls to £217.26/month (from £429.80). 2.7m UC claimants are assessed LCWRA. £3.5bn of employment support. WorkWell reaches 250,000 people. 65,000 already helped since Mar 2025. These are **support/offer counts, not moved-into-work** [V-para]. https://wired-gov.net/wg/news.nsf/articles/Thousands+to+be+supported+into+work+as+government+reforms+welfare+system+06042026122000?open=
- **No OBR-certified "number moved into work" from the 2025/26 welfare reforms was found [NOT FOUND].**
