SELECT round(SUM(d),5)
FROM (
	SELECT (open_bid-close_ask) d
	FROM (SELECT * FROM client0
		where is_open='false' and side='SELL') s1
	UNION
	SELECT (open_ask-close_bid) d
	FROM (SELECT * FROM client0
		where is_open='false' and side='BUY') s2
	) s3