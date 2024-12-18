from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import pendulum
import sys
import os

# plugins모듈 사용
sys.path.append('/code/plugins')
from link_crawling import main
local_tz = pendulum.timezone("Asia/Seoul")

default_args={
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=3),
    'email_on_failure': False
}# 추가로 default_args에 email, email_on_failure, execution_time(task 실행시간 제한) 등을 걸수 있음

with DAG (
    'dag_crawling_to_db',
    default_args = default_args, 
    max_active_runs=1,
    description='crawling data from job posting websites and store into S3 and Database',
    start_date=datetime(2024, 12, 18, tzinfo=local_tz),
    schedule='@daily', # 매일 자정 실행
    catchup=False,
    is_paused_upon_creation=False,  # DAG 자동 활성화
    tags=['url', 'crawling','db','S3','RDS'],
) as dag:

    link_crawl = PythonOperator(
    #link_crawl = BashOperator(
        task_id='link_crawl',
        python_callable=main
        #bash_command="python /code/plugins/link_crawling.py"
    )

    start = EmptyOperator(task_id="start") 
    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS) 

    # DAG 내 태스크 의존성 설정
    start >> link_crawl >> end

