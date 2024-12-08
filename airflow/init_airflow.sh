#!/bin/bash

# Airflow 데이터베이스 초기화
airflow db init || { echo "Database initialization failed"; exit 1; }

# Airflow 관리자 계정 생성
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin || { echo "Admin user creation failed"; exit 1; }

# 전달된 명령 실행
exec "$@"
