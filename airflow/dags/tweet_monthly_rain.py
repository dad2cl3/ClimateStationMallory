from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.utils.dates import days_ago
from pendulum import timezone
from datetime import datetime
from daily_tweets.monthly_rain_totals import build_monthly_rain_totals

local_tz = timezone('US/Eastern')

default_args = {
    'owner': 'pi',
}

dag_id = task_name = 'tweet_monthly_rain_totals'

with DAG(
    dag_id=dag_id,
    default_args=default_args,
    start_date=datetime(2021, 5, 5, tzinfo=local_tz),
    schedule_interval='0 8 * * *',
    concurrency=1,
    max_active_runs=1,
    catchup=False
) as dag:

    tweet_monthly_rain_totals = PythonOperator(
        task_id=task_name,
        python_callable=build_monthly_rain_totals,
        dag=dag
    )

    tweet_monthly_rain_totals