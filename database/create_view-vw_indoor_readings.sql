CREATE OR REPLACE VIEW weather.vw_indoor_readings AS
	SELECT
		JSONB_BUILD_OBJECT(
			'readings',
			JSONB_AGG(
				JSONB_BUILD_OBJECT(
					'reading_id',
					tr.reading_id,
					'reading_ts',
					(tr.reading_ts AT TIME ZONE 'US/Eastern'),
					'reading_device_channel',
					tr.reading_device_channel,
					'humidity',
					(tr.reading->>'humidity')::INTEGER,
					'temperature',
					(tr.reading->>'temperature_F')::DECIMAL
				)
			)
		) readings
	FROM weather.t_readings tr
	WHERE tr.reading_device_channel BETWEEN 1 AND 8
	AND tr.reading_ts AT TIME ZONE 'US/Eastern' >= DATE_TRUNC('DAY', (CURRENT_TIMESTAMP AT TIME ZONE 'US/Eastern' - INTERVAL '7 DAYS'));

--	DROP VIEW weather.vw_indoor_readings;