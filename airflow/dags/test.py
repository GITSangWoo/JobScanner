from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    'example_dag',  # DAG 이름
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval=timedelta(days=1),  # 매일 실행
    start_date=datetime(2023, 12, 1),  # 시작 날짜
    catchup=False,  # 지난 일정 실행 안 함
    is_paused_upon_creation=False,  # DAG 자동 활성화
) as dag:

    # 첫 번째 태스크: Hello World 출력
    def print_hello():
        print("Hello, Airflow!")

    task1 = PythonOperator(
        task_id='print_hello',
        python_callable=print_hello,
    )

    # 두 번째 태스크: 파일 생성
    def create_file():
        with open('/tmp/example_dag_file.txt', 'w') as f:
            f.write("This is a file created by Airflow DAG!")

    task2 = PythonOperator(
        task_id='create_file',
        python_callable=create_file,
    )

    # 태스크 순서 지정
    task1 >> task2

