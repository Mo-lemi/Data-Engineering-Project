-- Analysis queries for weather.db. Run them all with: python run_queries.py
-- Each query starts with a "-- Q" title line, which run_queries.py prints above the results.

-- Q1: Which city is warmest on average? (daily mean = average of max and min)
SELECT c.name AS city,
       ROUND(AVG((w.temp_max_c + w.temp_min_c) / 2), 1) AS avg_temp_c
FROM daily_weather w
JOIN cities c USING (city_id)
GROUP BY c.name
ORDER BY avg_temp_c DESC;

-- Q2: Which calendar month is wettest in each city? (average rainfall for that month over 5 years)
WITH monthly AS (
    SELECT c.name AS city,
           strftime('%m', w.date) AS month,
           ROUND(SUM(w.precipitation_mm) / COUNT(DISTINCT strftime('%Y', w.date)), 1) AS avg_rain_mm
    FROM daily_weather w
    JOIN cities c USING (city_id)
    GROUP BY city, month
),
ranked AS (
    SELECT city, month, avg_rain_mm,
           RANK() OVER (PARTITION BY city ORDER BY avg_rain_mm DESC) AS rank_in_city
    FROM monthly
)
SELECT city, month, avg_rain_mm
FROM ranked
WHERE rank_in_city = 1
ORDER BY city;

-- Q3: How many days above 30 degrees C did each city have per year?
SELECT c.name AS city,
       strftime('%Y', w.date) AS year,
       SUM(CASE WHEN w.temp_max_c > 30 THEN 1 ELSE 0 END) AS days_above_30c
FROM daily_weather w
JOIN cities c USING (city_id)
GROUP BY city, year
ORDER BY city, year;

-- Q4: Which city has the biggest gap between day and night temperatures?
SELECT c.name AS city,
       ROUND(AVG(w.temp_max_c - w.temp_min_c), 1) AS avg_daily_range_c
FROM daily_weather w
JOIN cities c USING (city_id)
GROUP BY c.name
ORDER BY avg_daily_range_c DESC;

-- Q5: Is it getting warmer? Average temperature across all five cities per year.
SELECT strftime('%Y', date) AS year,
       ROUND(AVG((temp_max_c + temp_min_c) / 2), 2) AS avg_temp_c
FROM daily_weather
GROUP BY year
ORDER BY year;
