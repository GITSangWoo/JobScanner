from airflow import DAG
from airflow.models import TaskInstance
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import timedelta
import pendulum
from discord_webhook import DiscordWebhook, DiscordEmbed
from typing import Optional 

from airflow.decorators import dag, task
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

import re
import sys, os
sys.path.append(os.getcwd())

from crawling.link_crawling import *

# 기본 UTC 시간에서 Asia/Seoul로 변경
local_tz = pendulum.timezone("Asia/Seoul")

TI = TaskInstance

def send_alert_discord(context):
	# Get Task Instances variables
	last_task: Optional[TaskInstance] = context.get('task_instance')
	task_name = last_task.task_id
	dag_name = last_task.dag_id
	log_link = last_task.log_url
	execution_date = str(context.get('execution_date'))

	# Extract reason for the exception
	try:
		error_message = str(context["exception"])
		error_message = error_message[:1000] + (error_message[1000:] and '...')
		str_start = re.escape("{'reason': ")
		str_end = re.escape('"}.')
		error_message = re.search('%s(.*)%s' % (str_start, str_end), error_message).group(1)
		error_message = "{'reason': " + error_message + '}'
	except:
		error_message = "Some error that cannot be extracted has occurred. Visit the logs!"

	# Send Alert
	#webhook = DiscordWebhook(url=Variable.get("discord_webhook")) # Update variable name with your change
	webhook = DiscordWebhook(url="https://discordapp.com/api/webhooks/1317043601112301579/NBlHm79BBz0FNl9oRccYGwi0aqzCNcdr1eylDXZauBkyTP-4b_IIPt9Ir2BLPIFt1dz3")
	embed = DiscordEmbed(title="Airflow Alert - Task has failed!", color='CC0000', url=log_link, timestamp=execution_date)
	embed.add_embed_field(name="DAG", value=dag_name, inline=True)
	embed.add_embed_field(name="PRIORITY", value="HIGH", inline=True)
	embed.add_embed_field(name="TASK", value=task_name, inline=False)
	embed.add_embed_field(name="ERROR", value=error_message)
	webhook.add_embed(embed)
	response = webhook.execute()

	return response

default_args={
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=3),
    'email_on_failure': False,
    'execution_timeout': timedelta(hours=2),  # 실행 시간 제한 설정
	'on_failure_callback': send_alert_discord
}# 추가로 default_args에 email, email_on_failure, execution_time(task 실행시간 제한) 등을 걸수 있음

with DAG (
    'crawling_pipeline',
    default_args = default_args, 
    max_active_runs=1,
    description='crawling data from job posting websites and store into S3 and Database',
    start_date=pendulum.datetime(2024, 12, 9, tz=local_tz),
    schedule_interval='@daily', # 매일 자정 실행
    catchup=False,
    tags=['crawling','db','S3','RDS'],
    is_paused_upon_creation=False,
) as dag:

    link_crawl = BashOperator(
        task_id='link_crawl',
        bash_command='python /opt/airflow/plugins/crawling/link_crawling.py',
    )

    trigger_preprocess = TriggerDagRunOperator(
		task_id='trigger_preprocess',
		trigger_dag_id='preprocess_pipeline',  # The DAG ID of dag_preprocess.py
		trigger_rule=TriggerRule.ALL_SUCCESS
	)

    start = EmptyOperator(task_id="start") 
    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ONE_SUCCESS) 

    # DAG 내 태스크 의존성 설정
    start >> link_crawl >> end >> trigger_preprocess
