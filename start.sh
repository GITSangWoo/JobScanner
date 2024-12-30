#!/bin/bash

#docker 컨테이너 실행 (시작X)
docker compose down
sleep 10
docker rmi finalrepo-link_crawler finalrepo-crawling-post_crawler finalrepo-crawling-text_crawler finalrepo-extract_crawler
sleep 10
docker compose up -d --no-start --force-recreate --build
sleep 5

# link_crawler 컨테이너 실행
#docker compose start link_crawler
echo "link_crawler 컨테이너 실행"
sleep 10

# link_crawler 종료 대기
#docker wait link_crawler
echo "link_crawler 컨테이너 작업 완료 및 종료"

# 1분 대기
sleep 30

# post_crawler 컨테이너 실행
docker compose start post_crawler
echo "post_crawler 컨테이너 실행"
sleep 10

# post_crawler 종료 대기
docker wait post_crawler
echo "post_crawler 컨테이너 작업 완료 및 종료"

# 1분 대기
sleep 30

# text_crawler 컨테이너 실행
docker compose start text_crawler
echo "text_crawler 컨테이너 실행"

sleep 10
# text_crawler 종료 대기
docker wait text_crawler
echo "text_crawler 컨테이너 작업 완료 및 종료"

# 1분 대기
sleep 30

# extract_crawler 컨테이너 실행
docker compose start extract_crawler
echo "extract_crawler 컨테이너 실행"

sleep 10
# extract_crawler 종료 대기
docker wait extract_crawler
echo "extract_crawler 컨테이너 작업 완료 및 종료"

