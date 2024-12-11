from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import pendulum
# from crawling.link_crawling import main

import os 
import sys
sys.path.append('/opt/airflow/plugins')
os.environ["CRAWLING_OUTPUT_DIR"] = "/opt/airflow/plugins/crawling"

# 기본 UTC 시간에서 Asia/Seoul로 변경
local_tz = pendulum.timezone("Asia/Seoul")

default_args={
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=3),
    'email_on_failure': False,
    'execution_timeout': timedelta(hours=2),  # 실행 시간 제한 설정
}# 추가로 default_args에 email, email_on_failure, execution_time(task 실행시간 제한) 등을 걸수 있음

with DAG (
    'crawling_pipeline',
    default_args = default_args, 
    max_active_runs=1,
    description='crawling data from job posting websites and store into S3 and Database',
    start_date=datetime(2024, 12, 9),
    schedule_interval='@daily', # 매일 자정 실행
    catchup=False,
    tags=['crawling','db','S3','RDS'],
) as dag:

    def link_crawling_task():
        from crawling.link_crawling import execute_link_crawlings
        execute_link_crawlings()

    link_crawl = PythonOperator(
        task_id='link_crawl',
        python_callable=link_crawling_task,
    )

    start = EmptyOperator(task_id="start") 
    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS) 

    # DAG 내 태스크 의존성 설정
    start >> link_crawl >> end

