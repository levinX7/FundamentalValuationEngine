-- 1) coverage
SELECT COUNT(*) AS forecast_rows, COUNT(DISTINCT ticker) AS tickers
FROM forecast;

-- 2) summary stats
SELECT
  ROUND(AVG(`forecast_change_%`), 2)   AS avg_forecast_change_pct,
  ROUND(AVG(forecast_price_30d), 2)    AS avg_forecast_price_30d,
  ROUND(AVG(forecast_market_cap_b), 2) AS avg_forecast_mcap_b
FROM forecast;

-- 3) top/bottom by expected % change
SELECT ticker, `forecast_change_%`
FROM forecast
ORDER BY `forecast_change_%` DESC
LIMIT 10;

SELECT ticker, `forecast_change_%`
FROM forecast
ORDER BY `forecast_change_%` ASC
LIMIT 10;

-- 4) price target (30d) vs current price
SELECT
  f.ticker,
  b.current_price,
  f.forecast_price_30d,
  ROUND(100.0 * (f.forecast_price_30d / NULLIF(b.current_price, 0) - 1), 2) AS price_upside_pct
FROM forecast f
JOIN basic_info b USING (ticker)
WHERE f.forecast_price_30d IS NOT NULL
  AND b.current_price IS NOT NULL
ORDER BY price_upside_pct DESC
LIMIT 20;

-- 5) forecast market cap vs current market cap
SELECT
  f.ticker,
  b.current_market_cap_b AS current_market_cap_b,
  f.forecast_market_cap_b,
  (f.forecast_market_cap_b - b.current_market_cap_b) AS diff_b,
  ROUND(100.0 * (f.forecast_market_cap_b / NULLIF(b.current_market_cap_b, 0) - 1), 2) AS diff_pct
FROM forecast f
JOIN basic_info b USING (ticker)
WHERE f.forecast_market_cap_b IS NOT NULL
  AND b.current_market_cap_b IS NOT NULL
ORDER BY diff_b DESC
LIMIT 20;

-- 6) sector view: average expected change
SELECT
  b.sector,
  COUNT(*) AS n,
  ROUND(AVG(`forecast_change_%`), 2) AS avg_forecast_change_pct
FROM forecast f
JOIN basic_info b USING (ticker)
GROUP BY b.sector
ORDER BY avg_forecast_change_pct DESC;