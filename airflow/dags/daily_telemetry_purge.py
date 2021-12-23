from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.utils.dates import days_ago
from pendulum import timezone
from datetime import datetime
# from daily_tweets.daily_rain_totals import build_daily_rain_totals
from daily_jobs.daily_telemetry_purge import perform_telemetry_purge
local_tz = timezone('US/Eastern')

default_args = {
    'owner': 'ubuntu',
}

dag_id = task_name = 'daily_telemetry_purge'

with DAG(
    dag_id=dag_id,
    default_args=default_args,
    start_date=datetime(2021, 5, 5, tzinfo=local_tz),
    schedule_interval='0 5 * * *',
    concurrency=1,
    max_active_runs=1,
    catchup=False
) as dag:

    daily_telemetry_purge = PythonOperator(
        task_id=task_name,
        python_callable=perform_telemetry_purge,
        dag=dag
    )

    daily_telemetry_purge
