CREATE OR REPLACE VIEW weather.vw_outdoor_readings AS
	SELECT
		JSONB_BUILD_OBJECT(
			'readings',
			JSONB_AGG(
				JSONB_BUILD_OBJECT(
					'reading_device_channel',
					tr.reading_device_channel,
					'reading',
					tr.reading
				)
			)
		) readings
	FROM weather.t_readings tr
	WHERE tr.reading_device_channel IN (0, 20, 21)
	-- WHERE tr.reading_device_channel = 0
	AND tr.reading_ts AT TIME ZONE 'US/Eastern' > DATE_TRUNC('DAY', (CURRENT_TIMESTAMP AT TIME ZONE 'US/Eastern' - INTERVAL '30 DAYS'));
	-- AND tr.reading_ts AT TIME ZONE 'US/Eastern' > DATE_TRUNC('DAY', (CURRENT_TIMESTAMP AT TIME ZONE 'US/Eastern' - INTERVAL '1 DAYS'));

-- DROP VIEW weather.vw_outdoor_readings;
