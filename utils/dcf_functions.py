YEARS = 4

# --------- Corrected Fields ---------
income_fields = ['Total Revenue', 'Operating Income', 'Pretax Income', 'Tax Provision']
cashflow_fields = ['Operating Cash Flow', 'Capital Expenditure', 'Free Cash Flow', 
                   'Depreciation And Amortization', 'Stock Based Compensation']
balance_fields = ['Current Assets', 'Current Liabilities', 'Cash And Cash Equivalents']

info_fields = ['beta', 'marketCap', 'sharesOutstanding', 'sector']



def get_financial_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Fetch financials
        income_stmt = ticker.financials.T.head(YEARS)
        cash_flow = ticker.cashflow.T.head(YEARS)
        balance_sheet = ticker.balance_sheet.T.head(YEARS)
        info = ticker.info

        # --- Income Statement ---
        for col in income_fields:
            if col not in income_stmt.columns:
                income_stmt[col] = pd.NA
                missing_log.append((ticker_symbol, 'Income Statement', col))
        income_df = income_stmt[income_fields].copy()
        income_df['Ticker'] = ticker_symbol

        # --- Cash Flow Statement ---
        for col in cashflow_fields:
            if col not in cash_flow.columns:
                cash_flow[col] = pd.NA
                missing_log.append((ticker_symbol, 'Cash Flow', col))
        cashflow_df = cash_flow[cashflow_fields].copy()
        cashflow_df['Ticker'] = ticker_symbol

        # --- Balance Sheet ---
        for col in balance_fields:
            if col not in balance_sheet.columns:
                balance_sheet[col] = pd.NA
                missing_log.append((ticker_symbol, 'Balance Sheet', col))
        balance_df = balance_sheet[balance_fields].copy()
        balance_df['Ticker'] = ticker_symbol

        # --- Info ---
        info_clean = {key: info.get(key, None) for key in info_fields}
        info_clean['Ticker'] = ticker_symbol
        info_df = pd.DataFrame([info_clean])

        return income_df, cashflow_df, balance_df, info_df

    except Exception as e:
        print(f"❌ Error with {ticker_symbol}: {e}")
        return None, None, None, None



def project_fcff_from_history(fcff_df, projection_years=3):
    projections_fcff = []

    # Growth caps per industry (you can tweak these)
    industry_growth_cap = {
        'Technology': 0.9,
        'Consumer Defensive': 0.06,
        'Consumer Cyclical': 0.07,
        'Healthcare': 0.08,
        'Industrials': 0.05,
        'Financial Services': 0.06,
        'Energy': 0.04,
        'Utilities': 0.03,
        'Basic Materials': 0.05,
        'Real Estate': 0.04,
        'Communication Services': 0.08
    }

    # Cache industry lookups to avoid redundant API calls
    industry_cache = {}

    def get_industry(ticker):
        if ticker in industry_cache:
            return industry_cache[ticker]
        try:
            info = yf.Ticker(ticker).info
            industry = info.get('sector', 'Unknown')
        except Exception:
            industry = 'Unknown'
        industry_cache[ticker] = industry
        return industry

    for ticker in fcff_df['Ticker'].unique():
        ticker_df = fcff_df[fcff_df['Ticker'] == ticker].sort_values('Date').tail(3)

        if len(ticker_df) < 3:
            continue

        fcff_vals = ticker_df['FCFF'].values

        # Avoid division by zero or erratic values
        if fcff_vals[0] == 0 or fcff_vals[1] == 0 or any(pd.isna(fcff_vals)):
            continue

        g1 = (fcff_vals[1] - fcff_vals[0]) / fcff_vals[0]
        g2 = (fcff_vals[2] - fcff_vals[1]) / fcff_vals[1]
        avg_growth = (g1 + g2) / 2

        # Lookup industry and apply cap
        industry = get_industry(ticker)
        cap = industry_growth_cap.get(industry, 0.06)  # fallback cap
        avg_growth = max(min(avg_growth, cap), 0.00)   # apply cap and floor

        last_fcff = fcff_vals[-1]
        last_year = pd.to_datetime(ticker_df['Date'].max()).year

        for i in range(1, projection_years + 1):
            future_year = last_year + i
            projected_fcff = last_fcff * ((1 + avg_growth) ** i)

            projections_fcff.append({
                'Ticker': ticker,
                'Year': future_year,
                'Projected FCFF': round(projected_fcff, 2),
                'Growth Rate': round(avg_growth, 4),
                'Industry': industry,
                'Cap Used': cap
            })

    return pd.DataFrame(projections_fcff)


def compute_capm_for_tickers(tickers, risk_free_rate=0.042, market_return=0.09):
    """
    Computes CAPM (Cost of Equity) for a list of tickers using beta from yfinance.
    """
    capm_results = []

    for ticker in tickers:
        try:
            yf_ticker = yf.Ticker(ticker)
            beta = yf_ticker.info.get('beta', None)

            if beta is not None:
                cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
            else:
                cost_of_equity = None

            capm_results.append({
                'Ticker': ticker,
                'Beta': round(beta, 3) if beta else None,
                'Cost of Equity (CAPM)': round(cost_of_equity, 4) if cost_of_equity else None
            })

        except Exception as e:
            capm_results.append({
                'Ticker': ticker,
                'Error': str(e)
            })

    return pd.DataFrame(capm_results)



def compute_cost_of_debt(ticker_symbol, tax_rate=None):
    """
    Computes cost of debt using:
    Cost of Debt = |Interest Expense| / Total Debt (from yfinance)
    Optionally returns after-tax cost of debt if tax_rate is provided.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Get Income Statement and Balance Sheet
        income_stmt = ticker.income_stmt.T
        balance_sheet = ticker.balance_sheet.T

        # Pull relevant data
        interest_expense = income_stmt.get('Interest Expense')
        total_debt = balance_sheet.get('Total Debt')

        # Handle missing data
        if interest_expense is None or total_debt is None:
            print(f"Missing data for {ticker_symbol}")
            return None

        # Use latest non-null values
        latest_interest = interest_expense.dropna().iloc[-1]
        latest_debt = total_debt.dropna().iloc[-1]

        if latest_debt == 0:
            return None  # avoid division by zero

        raw_cost = abs(latest_interest) / latest_debt
        cost_of_debt = round(raw_cost * (1 - tax_rate), 4) if tax_rate else round(raw_cost, 4)

        return cost_of_debt

    except Exception as e:
        print(f"Error for {ticker_symbol}: {e}")
        return None



def compute_wacc_using_existing_functions(ticker_symbol, capm_dict, tax_rate=0.21):
    try:
        ticker = yf.Ticker(ticker_symbol)

        # Cost of Equity from CAPM results
        cost_of_equity = capm_dict.get(ticker_symbol)
        if cost_of_equity is None:
            print(f"Missing CAPM for {ticker_symbol}")
            return None

        # Cost of Debt using your function
        cost_of_debt = compute_cost_of_debt(ticker_symbol, tax_rate=tax_rate)
        if cost_of_debt is None:
            print(f"Missing Cost of Debt for {ticker_symbol}")
            return None

        # Capital structure
        info = ticker.info
        equity = info.get('marketCap', None)
        balance_sheet = ticker.balance_sheet.T
        total_debt_series = balance_sheet.get('Total Debt')

        if equity is None or total_debt_series is None:
            print(f"Missing capital data for {ticker_symbol}")
            return None

        debt = total_debt_series.dropna().iloc[-1]
        total_value = equity + debt
        if total_value == 0:
            return None

        # Weighted Average Cost of Capital
        wacc = (equity / total_value) * cost_of_equity + (debt / total_value) * cost_of_debt
        return round(wacc, 4)

    except Exception as e:
        print(f"Error for {ticker_symbol}: {e}")
        return None


def run_dcf_for_tickers(tickers, fcff_df, tax_rate=0.21, risk_free_rate=0.042, market_return=0.09, projection_years=3, terminal_growth_rate=0.02):
    # Step 1: Compute cost of equity via CAPM
    capm_df = compute_capm_for_tickers(tickers, risk_free_rate, market_return)
    capm_dict = capm_df.set_index('Ticker')['Cost of Equity (CAPM)'].to_dict()
    
    # Step 2: Compute WACC per ticker
    wacc_results = []
    for t in tickers:
        wacc = compute_wacc_using_existing_functions(t, capm_dict, tax_rate)
        wacc_results.append({'Ticker': t, 'WACC': wacc})
    wacc_df = pd.DataFrame(wacc_results)

    # Step 3: Project FCFF
    projections_df = project_fcff_from_history(fcff_df, projection_years=projection_years)

    # Step 4: Calculate DCF using everything above
    dcf_results = []

    for ticker in tickers:
        # Get WACC
        wacc_row = wacc_df[wacc_df['Ticker'] == ticker]
        if wacc_row.empty:
            continue
        wacc = wacc_row['WACC'].values[0]
        if wacc is None or wacc == 0:
            continue

        # Get FCFF projections
        proj_rows = projections_df[projections_df['Ticker'] == ticker].sort_values('Year')
        projected_fcffs = proj_rows['Projected FCFF'].values

        if len(projected_fcffs) == 0:
            continue

        # Discount projected FCFFs
        discounted_fcffs = [fcff / ((1 + wacc) ** (i + 1)) for i, fcff in enumerate(projected_fcffs)]

        # Terminal value
        last_fcff = projected_fcffs[-1]
        terminal_value = (last_fcff * (1 + terminal_growth_rate)) / (wacc - terminal_growth_rate)
        discounted_terminal_value = terminal_value / ((1 + wacc) ** len(projected_fcffs))

        # Combine for enterprise value
        dcf_value = sum(discounted_fcffs) + discounted_terminal_value

        dcf_results.append({
            'Ticker': ticker,
            'DCF Value': round(dcf_value, 2),
            'WACC': round(wacc, 4),
            'Growth Rate': round(proj_rows['Growth Rate'].values[0], 4)
        })
    print(f"TV % of DCF: {discounted_terminal_value / (sum(discounted_fcffs) + discounted_terminal_value):.2%}")
    return pd.DataFrame(dcf_results)


