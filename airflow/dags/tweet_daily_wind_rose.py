from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.utils.dates import days_ago
from pendulum import timezone
from datetime import datetime
from daily_tweets.daily_wind_rose import build_daily_wind_rose

local_tz = timezone('US/Eastern')

default_args = {
    'owner': 'pi',
}

dag_id = task_name = 'tweet_daily_wind_rose'

with DAG(
    dag_id=dag_id,
    default_args=default_args,
    start_date=datetime(2021, 5, 5, tzinfo=local_tz),
    schedule_interval='0 8 * * *',
    concurrency=1,
    max_active_runs=1,
    catchup=False
) as dag:

    tweet_daily_rain_totals = PythonOperator(
        task_id=task_name,
        python_callable=build_daily_wind_rose,
        dag=dag
    )
