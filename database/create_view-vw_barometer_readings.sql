CREATE OR REPLACE VIEW weather.vw_barometer_readings AS
    SELECT
        JSONB_BUILD_OBJECT(
            'readings',
            JSONB_AGG(
                tr.reading
            )
        ) readings
    FROM weather.t_readings tr
    WHERE tr.reading_device_channel = 21
    AND tr.reading_ts AT TIME ZONE 'US/Eastern' > (CURRENT_TIMESTAMP AT TIME ZONE 'US/Eastern' - INTERVAL '3 HOURS');

-- DROP VIEW weather.vw_barometer_readings;