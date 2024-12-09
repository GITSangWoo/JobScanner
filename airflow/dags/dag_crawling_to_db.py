from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import pendulum

from crawling.link_crawling import *

# 기본 UTC 시간에서 Asia/Seoul로 변경
local_tz = pendulum.timezone("Asia/Seoul")

default_args={
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=3),
    'email_on_failure': False
}# 추가로 default_args에 email, email_on_failure, execution_time(task 실행시간 제한) 등을 걸수 있음

with DAG (
    'crawling_to_database',
    default_args = default_args, 
    max_active_runs=1,
    description='crawling data from job posting websites and store into S3 and Database',
    start_date=datetime(2024, 12, 9),
    schedule_interval='@daily', # 매일 자정 실행
    catchup=False,
    tags=['crawling','db','S3','RDS'],
) as dag:
    # 인크루트
    incruit_link_task = PythonOperator(
        task_id='incruit_link_task',
        python_callable=incruit_link(),
    )

    # 잡코리아
    jobkorea_link_task = PythonOperator(
        task_id='jobkorea_link_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jobkorea/link_scrape.py'
    )

    # 점핏
    jumpit_link_task = BashOperator(
        task_id='jumpit_link_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jumpit/jumpit_links.py'
    )

    # 로켓펀치
    rocketpunch_main_task = BashOperator(
        task_id='rocketpunch_main_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/rocketpunch/main.py'
    )

    # 사람인
    saramin_url_task = BashOperator(
        task_id='saramin_url_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/saramin/saramin_url_crawling.py'
    )

    # 원티드
    wanted_joblog_task = BashOperator(
        task_id='wanted_joblog_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/wanted/makejoblog.py'
    )

    start = EmptyOperator(task_id="start") 
    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS) 

    # DAG 내 태스크 의존성 설정
    start >> [incruit_link_task, jobkorea_link_task, jumpit_link_task, rocketpunch_main_task, saramin_url_task, wanted_joblog_task]
    [incruit_link_task, jobkorea_link_task, jumpit_link_task, rocketpunch_main_task, saramin_url_task, wanted_joblog_task] >> end

    

