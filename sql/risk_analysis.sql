-- 1) coverage
SELECT COUNT(*) AS risk_rows, COUNT(DISTINCT ticker) AS tickers
FROM risk;

-- 2) summary stats
SELECT
  ROUND(AVG(cumulative_return), 4)     AS avg_cum_return,
  ROUND(AVG(annualized_return), 4)     AS avg_ann_return,
  ROUND(AVG(annualized_volatility), 4) AS avg_ann_vol,
  ROUND(AVG(sharpe_ratio), 4)          AS avg_sharpe
FROM risk;

-- 3) best/worst Sharpe
SELECT ticker, sharpe_ratio
FROM risk
ORDER BY sharpe_ratio DESC
LIMIT 10;

SELECT ticker, sharpe_ratio
FROM risk
ORDER BY sharpe_ratio ASC
LIMIT 10;

-- 4) low/high volatility
SELECT ticker, annualized_volatility
FROM risk
ORDER BY annualized_volatility ASC
LIMIT 10;

SELECT ticker, annualized_volatility
FROM risk
ORDER BY annualized_volatility DESC
LIMIT 10;

-- 5) high return with capped volatility (tweak threshold)
SELECT
  ticker,
  annualized_return,
  annualized_volatility,
  sharpe_ratio
FROM risk
WHERE annualized_volatility <= 0.35
ORDER BY annualized_return DESC
LIMIT 20;

-- 6) sector risk summary
SELECT
  b.sector,
  COUNT(*) AS n,
  ROUND(AVG(annualized_return), 4)     AS avg_ann_return,
  ROUND(AVG(annualized_volatility), 4) AS avg_ann_vol,
  ROUND(AVG(sharpe_ratio), 4)          AS avg_sharpe
FROM risk r
JOIN basic_info b USING (ticker)
GROUP BY b.sector
ORDER BY avg_sharpe DESC;