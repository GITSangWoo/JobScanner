FROM node:12.22.9

WORKDIR /app

COPY package*.json . 

RUN npm install

COPY . .

# 환경 변수 설정
ENV HOST=0.0.0.0

EXPOSE 3000

CMD ["npm", "start"]

