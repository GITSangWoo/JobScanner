import os
import mysql.connector
from mysql.connector import Error
import json

# RDS MySQL 연결 정보
host = 't2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com'
port = 3306
user = 'admin'
password = 'dltkddn1'
database = 'service'

# 현재 파일(add_tech.py)의 디렉토리 경로를 기준으로 상대 경로 계산
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로 가져오기
json_file_path = os.path.join(current_file_dir, "../../../tech/tech_book.json")  # 상대 경로 계산

# MySQL 연결
connection = None  # connection 초기화
cursor = None  # cursor 초기화

try:
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

    if connection.is_connected():

        # JSON 파일 로드
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON 파일을 찾을 수 없습니다: {json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            tech_data = json.load(file)

        # 기술 스택 리스트의 키 값만 추출
        tech_stack_list = list(tech_data.keys())

        # 커서 생성
        cursor = connection.cursor()

        # 데이터 삽입 쿼리 준비
        insert_query = """
        INSERT INTO tech_stack (tech_name, tech_description)
        VALUES (%s, %s)
        """

        # 데이터 삽입
        for tech in tech_stack_list:
            cursor.execute(insert_query, (tech, "-"))

        # 변경 사항 커밋
        connection.commit()
        print(f"{len(tech_stack_list)}개의 기술 스택이 삽입되었습니다.")

except Error as e:
    print(f"에러 발생: {e}")
except FileNotFoundError as fe:
    print(fe)
except json.JSONDecodeError:
    print("JSON 파일 형식이 잘못되었습니다.")
finally:
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
