from airflow import DAG
from airflow.models import Variable, TaskInstance
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import timedelta
import pendulum
from discord_webhook import DiscordWebhook, DiscordEmbed
from typing import Optional 

import re
import sys
sys.path.append('/opt/airflow/plugins')

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
    'preprocess_pipeline',
    default_args = default_args, 
    max_active_runs=1,
    description='preprocess: transform image to text and extract tech stack',
    start_date=pendulum.datetime(2024, 12, 16, tz=local_tz),
    schedule_interval='@daily', # 매일 자정 실행
    catchup=False,
    tags=['preprocess','db','RDS'],
    is_paused_upon_creation=False,
) as dag:
	
    text_to_rqp = BashOperator(
		task_id='text.to.rqp',
        bash_command='python /opt/airflow/plugins/extract/tech/techextracttext.py',
    )
	
    ocr_task = BashOperator(
		task_id='ocr.task',
        bash_command='python /opt/airflow/plugins/extract/ocr/imagetotext.py',
    )
		
    image_to_rqp = BashOperator(
		task_id='image.to.rqp',
        bash_command='python /opt/airflow/plugins/extract/tech/techextractimg.py',
    )
	    
    start = EmptyOperator(task_id="start") 
    end = EmptyOperator(task_id="end", trigger_rule=TriggerRule.ALL_SUCCESS)
	
    start >> text_to_rqp >> end
    start >> ocr_task >>  image_to_rqp  >> end
	
    # 직무별 스택 취합, 날짜별, 기업별은 나중에 추가
	# 추후 extract_tech_table과 combined_table join 해서 위의 결과들 추출해서 table에 저장
	
    # 추가로 맨처음에 db접속 가능한지 detect하는 task 넣으면 좋을 듯
