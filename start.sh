#!/bin/bash

# link_crawler 컨테이너 실행
docker compose up -d --no-start
docker compose start link_crawler
echo "link_crawler 컨테이너 실행 완료"

# link_crawler 종료 대기
docker wait link_crawler
echo "link_crawler 컨테이너 작업 완료 및 종료"

# 1분 대기
sleep 60

# post_crawler 컨테이너 실행
docker compose start post_crawler
echo "post_crawler 컨테이너 실행 완료"

# post_crawler 종료 대기
docker wait post_crawler
echo "post_crawler 컨테이너 작업 완료 및 종료"

# 1분 대기
sleep 60

# text_crawler 컨테이너 실행
docker compose start text_crawler
echo "text_crawler 컨테이너 실행 완료"

# text_crawler 종료 대기
docker wait text_crawler
echo "text_crawler 컨테이너 작업 완료 및 종료"
