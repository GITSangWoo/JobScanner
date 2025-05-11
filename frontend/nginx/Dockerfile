# Step 1: 리액트 앱 빌드
FROM node:12.22.9 AS build 
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build

# Step 2: nginx 설정
FROM nginx:1.25.1
# nginx 기본 설정 파일 덮어쓰기
COPY ["default.conf","/etc/nginx/conf.d/"]
# 빌드된 리액트 앱을 nginx 컨테이너에 복사
COPY --from=build /app/build /usr/share/nginx/html
# 80번 포트 열기
EXPOSE 80
# nginx 실행
CMD ["nginx", "-g", "daemon off;"]

