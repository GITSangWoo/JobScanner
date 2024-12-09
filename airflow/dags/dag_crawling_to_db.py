from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta
import pendulum

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
    start_date=datetime(2024, 12, 3),
    schedule_interval='@daily', # 매일 자정 실행
    catchup=False,
    tags=['crawling','db','S3','RDS'],
) as dag:

    # 인크루트
    incruit_link_task = BashOperator(
        task_id='incruit_link_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/incruit/incruit_links.py'
    )

    incruit_crawling_task = BashOperator(
        task_id='incruit_crawling_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/incruit/incruit_crawling.py'
    )

    incruit_process_task = BashOperator(
        task_id='incruit_process_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/incruit/incruit_preprocess.py'
    )

    # 잡코리아
    jobkorea_link_task = BashOperator(
        task_id='jobkorea_link_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jobkorea/link_scrape.py'
    )

    jobkorea_crawling_task = BashOperator(
        task_id='jobkorea_crawling_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jobkorea/jobkorea_crawling.py'
    )

    jobkorea_spark_task = BashOperator(
        task_id='jobkorea_spark_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jobkorea/spark_division.py'
    )

    # 점핏
    jumpit_link_task = BashOperator(
        task_id='jumpit_link_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jumpit/jumpit_links.py'
    )

    jumpit_crawling_task = BashOperator(
        task_id='jumpit_crawling_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jumpit/jumpit_crawling.py'
    )

    jumpit_process_task = BashOperator(
        task_id='jumpit_process_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/jumpit/jumpit_preprocess.py'
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

    saramin_data_task = BashOperator(
        task_id='saramin_data_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/saramin/saramin_data_crawling.py'
    )

    saramin_detail_task = BashOperator(
        task_id='saramin_detail_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/saramin/saramin_detail.py'
    )

    # 원티드
    wanted_joblog_task = BashOperator(
        task_id='wanted_joblog_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/wanted/makejoblog.py'
    )

    wanted_crawl_task = BashOperator(
        task_id='wanted_crawl_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/wanted/wantedcrawl.py'
    )

    wanted_extract_task = BashOperator(
        task_id='wanted_extract_task',
        bash_command='python3 /home/dohyun/codes/DE32-final/crawling/wanted/wantedextract.py'
    )

    start = EmptyOperator(task_id="start") 
    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS) 

    # DAG 내 태스크 의존성 설정
    start >> [incruit_link_task, jobkorea_link_task, jumpit_link_task, rocketpunch_main_task, saramin_url_task, wanted_joblog_task]
    
    incruit_link_task >> incruit_crawling_task >> incruit_process_task
    jobkorea_link_task >> jobkorea_crawling_task >> jobkorea_spark_task
    jumpit_link_task >> jumpit_crawling_task >> jumpit_process_task
    rocketpunch_main_task
    saramin_url_task >> saramin_data_task >> saramin_detail_task
    wanted_joblog_task >> wanted_crawl_task >> wanted_extract_task

    [incruit_process_task, jobkorea_spark_task, jumpit_process_task, rocketpunch_main_task, saramin_detail_task, wanted_extract_task] >> end

    

