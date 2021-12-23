from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from hourly_tweets.hourly_conditions import build_current_conditions
import pendulum

# import os, sys

# sys.path.append(os.path.dirname('./'))
local_tz = pendulum.timezone('US/Eastern')

default_args = {
    'owner': 'pi'
}

dag_id = task_name = 'tweet_current_conditions'

with DAG(
    dag_id=dag_id,
    default_args=default_args,
    start_date=datetime(2021, 5, 5, tzinfo=local_tz),
    schedule_interval='0 9,12,15,18,21 * * *',
    concurrency=1,
    max_active_runs=1,
    catchup=False
) as dag:

    tweet_current_conditions = PythonOperator(
        task_id=task_name,
        python_callable=build_current_conditions,
        dag=dag
    )

    tweet_current_conditions