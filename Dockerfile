# Base image with Python 3.10
FROM python:3.10-slim

# 작업 디렉토리 설정
WORKDIR /code

# Root 사용자로 필요한 시스템 패키지 설치
USER root
RUN apt-get update && apt-get install -y \
    bash curl wget vim gnupg unzip \
    libnss3 libatk-bridge2.0-0 libgconf-2-4 libxss1 libxcomposite1 libxrandr2 libasound2 libvulkan1 \
    libxdamage1 libgbm-dev libgtk-3-0 libvulkan1 fonts-liberation libappindicator3-1 xdg-utils \
    default-mysql-client \
    default-libmysqlclient-dev gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Google Chrome 설치
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# Dockerfile 위치의 디렉토리 컨테이너 /code/디렉토리에 복사
COPY . /code

ENV TZ=Asia/Seoul

# python pdm 패키지 설치
RUN pip install --no-cache-dir -r /code/requirements.txt

# Shared memory configuration (required for Chrome)
RUN mkdir -p /dev/shm && chmod 777 /dev/shm
