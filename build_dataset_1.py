# AF3020 Research Project - Data Collection Script
# Topic: Empirical Evaluation of Black-Scholes via IV-RV Spread on FTSE 100
# Run: python3 build_dataset.py
# Requires: pip install yfinance pandas numpy openpyxl

import yfinance as yf
import pandas as pd
import numpy as np

print("Downloading data from Yahoo Finance...")
print("This will take about 30 seconds...\n")

ftse  = yf.download("^FTSE",  start="2018-01-01", end="2023-12-31", auto_adjust=True, progress=False)
vftse = yf.download("^VFTSE", start="2018-01-01", end="2023-12-31", auto_adjust=True, progress=False)
vix   = yf.download("^VIX",   start="2018-01-01", end="2023-12-31", auto_adjust=True, progress=False)

print(f"FTSE rows downloaded:  {len(ftse)}")
print(f"VFTSE rows downloaded: {len(vftse)}")
print(f"VIX rows downloaded:   {len(vix)}")

for df_raw in [ftse, vftse, vix]:
    if isinstance(df_raw.columns, pd.MultiIndex):
        df_raw.columns = df_raw.columns.get_level_values(0)

ftse_close  = ftse['Close'].copy()
vftse_close = vftse['Close'].copy()
vix_close   = vix['Close'].copy()

log_returns = np.log(ftse_close / ftse_close.shift(1))
rv_21 = log_returns.rolling(window=21).std() * np.sqrt(252) * 100
rv_63 = log_returns.rolling(window=63).std() * np.sqrt(252) * 100

df = pd.DataFrame({
    'FTSE_Close': ftse_close,
    'VFTSE_IV':   vftse_close,
    'RV_21d':     rv_21,
    'RV_63d':     rv_63,
    'VIX':        vix_close,
})

df = df.dropna()
df.index.name = 'Date'
df = df.reset_index()

df['IV_RV_Spread']  = df['VFTSE_IV'] - df['RV_21d']
df['VIX_Lag1']      = df['VIX'].shift(1)
df['Crisis_Dummy']  = 0
df.loc[(df['Date'] >= '2020-02-01') & (df['Date'] <= '2020-05-31'), 'Crisis_Dummy'] = 1
df.loc[(df['Date'] >= '2022-01-01') & (df['Date'] <= '2022-12-31'), 'Crisis_Dummy'] = 1
df['VoV']           = df['VFTSE_IV'].rolling(window=21).std()
df['IV_Lag1']       = df['VFTSE_IV'].shift(1)
df['RV_Term_Slope'] = df['RV_21d'] - df['RV_63d']
df['Time_Trend']    = range(1, len(df) + 1)

df = df.dropna().reset_index(drop=True)

print(f"\n{'='*55}")
print(f"FINAL DATASET SUMMARY")
print(f"{'='*55}")
print(f"Total observations:  {len(df)}")
print(f"Date range:          {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"\nIV_RV_Spread (dependent variable):")
print(f"  Mean:   {df['IV_RV_Spread'].mean():.3f}")
print(f"  Std:    {df['IV_RV_Spread'].std():.3f}")
print(f"  Min:    {df['IV_RV_Spread'].min():.3f}")
print(f"  Max:    {df['IV_RV_Spread'].max():.3f}")

key_cols = ['IV_RV_Spread', 'VFTSE_IV', 'RV_21d', 'VIX_Lag1', 'VoV', 'RV_Term_Slope']
print(f"\nDESCRIPTIVE STATISTICS:")
print(df[key_cols].describe().round(3).to_string())

stata_cols = [
    'Date', 'FTSE_Close', 'VFTSE_IV', 'RV_21d', 'RV_63d', 'VIX',
    'IV_RV_Spread', 'VIX_Lag1', 'Crisis_Dummy', 'VoV',
    'IV_Lag1', 'RV_Term_Slope', 'Time_Trend'
]

var_defs = pd.DataFrame({
    'Variable': stata_cols,
    'Role': [
        'Index', 'Control', 'Raw IV', 'Constructed RV', 'Constructed RV', 'Raw Data',
        'DEPENDENT VARIABLE',
        'Independent Variable 1', 'Independent Variable 2', 'Independent Variable 3',
        'Independent Variable 4', 'Independent Variable 5', 'Independent Variable 6'
    ],
    'Description': [
        'Trading date',
        'FTSE 100 index closing price level',
        'FTSE 100 Volatility Index - market-implied volatility (% annualised)',
        '21-day rolling realised volatility from FTSE 100 log returns (% annualised)',
        '63-day rolling realised volatility from FTSE 100 log returns (% annualised)',
        'CBOE VIX index daily closing level',
        'IV minus RV: measures Black-Scholes mispricing. Positive = BS overprices.',
        'VIX index lagged one trading day - global risk sentiment proxy',
        'Binary: 1 during COVID crash Feb-May 2020 and 2022 rate hike cycle',
        '21-day rolling standard deviation of VFTSE_IV - volatility uncertainty',
        'VFTSE_IV lagged one trading day - tests IV persistence',
        '21-day RV minus 63-day RV - volatility term structure slope',
        'Sequential integer 1 to N - captures secular trend across sample'
    ],
    'Source': [
        '-', 'Yahoo Finance ^FTSE', 'Yahoo Finance ^VFTSE',
        'Calculated from ^FTSE log returns', 'Calculated from ^FTSE log returns',
        'Yahoo Finance ^VIX', 'Constructed: VFTSE_IV - RV_21d',
        'Yahoo Finance ^VIX shifted 1 day', 'Author-defined stress periods',
        'Rolling std of VFTSE_IV 21-day', 'Yahoo Finance ^VFTSE shifted 1 day',
        'Constructed: RV_21d - RV_63d', 'Constructed integer sequence'
    ],
    'Expected_Sign': [
        '-', '-', '-', '-', '-', '-', 'n/a (DV)',
        '+', '+', '+', '+', '-', '?'
    ]
})

desc_stats = df[key_cols].describe().round(4)

output_path = "BS_FTSE_Dataset.xlsx"
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df[stata_cols].to_excel(writer, sheet_name='STATA_Import', index=False)
    desc_stats.to_excel(writer, sheet_name='Descriptive_Stats')
    var_defs.to_excel(writer, sheet_name='Variable_Definitions', index=False)

print(f"\nFILE SAVED: {output_path}")
print("Next: import STATA_Import sheet into STATA")
