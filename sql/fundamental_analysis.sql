-- Count of buy recommendations
SELECT `buy?`, COUNT(*) AS count
FROM fundamental
GROUP BY `buy?`;

-- Average market caps by buy flag
SELECT `buy?`,
       AVG(mutliples_market_cap_b) AS avg_multiples,
       AVG(ddm_market_cap_b) AS avg_ddm,
       AVG(dcf_market_cap_b) AS avg_dcf
FROM fundamental
GROUP BY `buy?`;

-- Top 10 highest median market caps where buy? = 1
SELECT ticker, median_market_cap_b
FROM fundamental
WHERE `buy?` = 1
ORDER BY median_market_cap_b DESC
LIMIT 10;

-- Compare DCF vs Multiples estimates
SELECT ticker,
       multiples_market_cap_b,
       dcf_market_cap_b,
       (dcf_market_cap_b - multiples_market_cap_b) AS dcf_minus_multiples
FROM fundamental
ORDER BY dcf_minus_multiples DESC
LIMIT 10;

SELECT
    f.ticker,
    f.fundamental_id,
    f.median_market_cap_b AS fair_value_b,
    b.current_market_cap_b AS current_market_cap_b,
    (f.median_market_cap_b - b.current_market_cap_b) AS diff_b,
    ROUND(100.0 * (f.median_market_cap_b / NULLIF(b.current_market_cap_b, 0) - 1), 2) AS diff_pct,
    f.`buy?` AS buy_flag
FROM fundamental f
JOIN basic_info b USING (ticker)
WHERE f.median_market_cap_b IS NOT NULL
  AND b.current_market_cap_b IS NOT NULL
ORDER BY diff_b DESC;