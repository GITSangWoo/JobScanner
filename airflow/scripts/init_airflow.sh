#!/bin/bash

# fernet_key 설정, 암호화 데이터 보호
if [ -z "$AIRFLOW__CORE__FERNET_KEY" ]; then
  export AIRFLOW__CORE__FERNET_KEY=$(openssl rand -base64 32)
  echo "Generated Fernet Key: $AIRFLOW__CORE__FERNET_KEY"
fi

# 디렉토리 생성
for DIR in /code/plugins/incruit /code/plugins/wanted /code/plugins/jumpit /code/plugins/logs; do
  if [ ! -d "$DIR" ]; then
    sudo mkdir -p "$DIR"
  fi
done

# 권한 설정
chown -R 1000:1000 /code/logs /code/plugins /code/plugins/logs

# 데이터베이스 초기화
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
