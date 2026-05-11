# Black-Scholes Empirical Evaluation — FTSE 100 Index Options

An empirical analysis of Black-Scholes model mispricing on FTSE 100 index options, using the implied-realised volatility (IV-RV) spread as the primary measure of model failure. Final year research project, BSc Accounting and Finance, University of Leicester (2026).

## Research Question

> Does Black-Scholes systematically misprice FTSE 100 index options through its constant volatility assumption, as evidenced by the spread between implied and realised volatility?

## Key Findings

- Mean IV-RV spread of **5.79 percentage points** over 2018–2023, indicating systematic Black-Scholes overpricing
- Global risk sentiment (VIX) is the primary driver of the spread — a 1pp increase in VIX widens the spread by **0.38pp** the following day
- Volatility of volatility exerts a significant **negative** effect, reflecting spread compression during extreme realised volatility spikes (e.g. March 2020)
- A significant positive **time trend** suggests the volatility risk premium has gradually widened over the sample period
- Crisis period dummy is insignificant — crisis effects are fully mediated by VIX

## Methodology

- **Dependent variable:** IV-RV Spread = VIX − 21-day rolling realised volatility (annualised, %)
- **Model:** OLS regression with Newey-West standard errors (lag=5) correcting for autocorrelation and heteroskedasticity
- **Diagnostic tests:** Durbin-Watson (DW = 0.272, severe autocorrelation), White's test (χ² = 863.58, p = 0.000)
- **Sample:** 1,397 daily observations, January 2018 – December 2023
- **Software:** Python (data collection), Stata/BE 19.0 (econometric estimation)

## Regression Results (Newey-West, lag=5)

| Variable | Coefficient | Std. Error | t-stat | p-value |
|---|---|---|---|---|
| VIX (lagged 1 day) | 0.381 | 0.073 | 5.23 | 0.000*** |
| Crisis Dummy | 0.289 | 0.933 | 0.31 | 0.757 |
| Volatility of Volatility | -1.038 | 0.431 | -2.41 | 0.016** |
| RV Term Slope | -0.282 | 0.151 | -1.86 | 0.063* |
| Time Trend | 0.002 | 0.001 | 4.23 | 0.000*** |
| Constant | -1.487 | 1.079 | -1.38 | 0.169 |

N = 1,397 | F(5, 1391) = 22.09 | R² = 0.261

*\*\*\* p<0.01, \*\* p<0.05, \* p<0.10*

## Variable Definitions

| Variable | Description |
|---|---|
| IV_RV_Spread | VIX minus 21-day rolling realised volatility (pp, annualised) — dependent variable |
| VIX_Lag1 | CBOE VIX index lagged one trading day — global risk sentiment proxy |
| Crisis_Dummy | 1 during COVID crash (Feb–May 2020) and 2022 rate hike cycle (Jan–Dec 2022) |
| VoV | 21-day rolling std of VIX — volatility of volatility |
| RV_Term_Slope | 21-day RV minus 63-day RV — volatility term structure slope |
| Time_Trend | Sequential integer 1–1,397 — secular trend |

## Data Sources

- **FTSE 100 index:** Yahoo Finance (`^FTSE`) — used to construct realised volatility from daily log returns
- **Implied volatility proxy:** CBOE VIX (`^VIX`) via Yahoo Finance — used as global IV benchmark
- **Sample period:** 1 January 2018 – 31 December 2023
- **Observations:** 1,397 trading days after rolling window construction

Data collected using Python (`yfinance` library). See `build_dataset.py` for full data collection and variable construction code.

## Repository Structure

```
black-scholes-ftse100-evaluation/
│
├── build_dataset.py          # Data collection and variable construction (Python)
├── BS_FTSE_Dataset.csv       # Final dataset used in Stata estimation
└── README.md
```

## Requirements

```bash
pip install yfinance pandas numpy openpyxl
```

## Related Projects

- [options-pricing](https://github.com/awaisdotnet/options-pricing) — Black-Scholes options pricer with Monte Carlo simulation
- [implied-volatility](https://github.com/awaisdotnet/implied-volatility) — Implied volatility solver with volatility smile visualisation
