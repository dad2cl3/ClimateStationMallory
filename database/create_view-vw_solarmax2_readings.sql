CREATE OR REPLACE VIEW weather.vw_solarmax2_readings AS
	SELECT
		JSONB_BUILD_OBJECT(
			'readings',
			JSONB_AGG(
				JSONB_BUILD_OBJECT(
					'reading_id',
					tr.reading_id,
					'reading_ts',
					(tr.reading_ts AT TIME ZONE 'US/Eastern'),
					'reading',
					tr.reading
				)
			)
		) readings
	FROM weather.t_readings tr
	WHERE tr.reading_device_channel = 30
	AND tr.reading_ts AT TIME ZONE 'US/Eastern' >= DATE_TRUNC('DAY', (CURRENT_TIMESTAMP AT TIME ZONE 'US/Eastern' - INTERVAL '7 DAYS'));

-- DROP VIEW weather.vw_solarmax2_readings;
