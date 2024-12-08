#!/bin/bash

# Airflow 데이터베이스 초기화
airflow db init

# Airflow 관리자 계정 생성
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Airflow 웹서버 실행
exec "$@"

