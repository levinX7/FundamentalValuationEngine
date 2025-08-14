# FundamentalValuationEngine

Presentation Link: https://www.canva.com/design/DAGwB0pRcNM/uw0gnIgCuY55244dWnSbcg/edit?utm_content=DAGwB0pRcNM&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton


# Levin Investments – Stock Picking & Valuation Tool

## Overview
This project is a **data-driven stock picking and valuation system** built with **Python**, **SQL**, and **Tableau**.  
It combines **fundamental analysis**, **risk metrics**, and **short-term forecasting** to identify undervalued, low-risk stocks from a pool of 300 randomly selected tickers.

The workflow:
- Pulls raw financial data from Yahoo Finance via `yfinance`
- Enriches & cleans data for modeling
- Runs multiple valuation models
- Measures risk and expected short-term movement
- Queries results in SQL for deeper insights
- Visualizes findings in Tableau dashboards

---

## Goal
Identify **data-driven investment opportunities** by:
- Valuing companies using **DCF**, **DDM**, and **Multiples**.
- Assessing risk with volatility, Sharpe ratio, and ARIMA-based 30-day price forecasts.
- Ranking and selecting stocks that are:
  - **Undervalued** (Median Market Cap > Current Market Cap)
  - **Low risk**
  - **Positive expected growth** in the short term

**Investor persona**:
- Low risk tolerance
- No sector bias
- No dividend preference

---

## Project Pipeline

### 1. Data Loading (Python in Jupyter Lab)
Extracted:
- Income Statement
- Balance Sheet
- Cash Flow Statement
- Historical stock prices

Collected additional firm metadata:
- Sector
- Beta
- Market Cap
- Shares Outstanding

Created structured DataFrames:
- `valuation` – Outputs from DCF, DDM, Multiples
- `risk` – Volatility, Sharpe ratio, returns
- `basic_info` – Sector, beta, market cap, shares
- `forecast` – ARIMA 30-day price predictions

> **Note:** Due to `yfinance` behavior, calling the data extraction and enrichment functions directly from `.py` scripts caused inconsistent results (API call failures, missing attributes). To ensure reproducibility, I kept the main workflow in **Jupyter Notebooks**.

---

### 2. Data Enrichment
- Calculated **Free Cash Flow to Firm (FCFF)** for the past 4 years.
- Projected **future FCFF** using 3-year CAGR, capped at **industry-specific growth rates**.
- Computed:
  - CAPM cost of equity
  - Cost of debt
  - WACC
- Valuation models:
  - Discounted Cash Flow (DCF)
  - Dividend Discount Model (DDM) (for dividend-paying stocks)
  - Multiples valuation (EV/EBITDA by sector)
- Combined valuations into a **Median Market Cap** metric.

---

### 3. Risk Analysis
Metrics:
- Annualized Return
- Annualized Volatility
- Sharpe Ratio
- Cumulative Return

Price Forecast:
- ARIMA(5,1,0) model, 30 trading days ahead.

Calculated:
- Forecast Change %
- Forecast Market Cap

---

### 4. SQL Analysis
Exported all cleaned/enriched DataFrames to SQL for:
- Grouped sector summaries
- Correlation analysis
- Statistical testing:
  - **T-Test (one-sided)**: Buy vs Non-Buy annualized returns → No significant difference
  - **Pearson correlation**: Annualized return vs volatility → No significant correlation

---

### 5. Exploratory Data Analysis (EDA)
- Cleaned column names, merged datasets, dropped nulls
- Ran `.describe()`, `.info()`, correlations
- Visualized:
  - Risk vs size scatter plots
  - Sector % composition
  - Top undervalued companies by value gap
  - Forecasted price changes

---

### 6. Visualization (Tableau)
Built interactive dashboards:
- Risk vs Size
- Forecasted Price Changes
- Sector breakdown of buy opportunities
- Football field chart for valuations
- Top undervalued stocks

---

## Key Findings
- No clear correlation between volatility and firm size.
- Consumer cyclical/defensive sectors = 35% of buy opportunities.
- Industrial firms = 32% of no-buy opportunities.
- Top undervalued stocks concentrated in Communication Services and Healthcare.
- Statistical tests showed **no evidence** that Buy stocks outperform Non-Buy stocks significantly (given sample size).

---

## Assumptions

### Financial Modeling:
- Projection years: 3 for FCFF
- Industry growth caps:
  - Technology: 9%
  - Energy: 4%
  - Utilities: 3%
  - etc.
- Tax rate: Default 21% if missing in data
- Terminal growth rate (DCF): 2%
- Risk-free rate: 4.2% (CAPM)
- Market return: 9% (CAPM)
- WACC: Weighted by market value of debt/equity, using most recent available figures

### Data Handling:
- Missing financial statement fields → filled with `NaN` (excluded from calculations)
- Beta missing → excluded from CAPM
- EBITDA missing for multiples → stock excluded from multiples valuation
- ARIMA only run if at least 60 daily closing prices were available

---

## Tech Stack
- **Python**: `pandas`, `numpy`, `yfinance`, `statsmodels`, `matplotlib`
- **SQL**: PostgreSQL for structured querying and hypothesis testing
- **Tableau**: For interactive dashboards
- **Jupyter Lab**: Development environment (due to `yfinance` reliability issues in `.py` scripts)

---

## Future Improvements
1. Use ML to estimate valuation model assumptions (e.g., WACC).
2. Integrate ChatGPT API for qualitative firm analysis.
3. Automate Tableau dashboard refresh via ETL jobs.
4. Expand universe of stocks and allow user-defined filters.