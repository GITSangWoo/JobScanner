import pymysql
import re
import json
import os

# 이미지에서 추출된 텍스트 데이터 기술 스택 추출


# RDS MySQL 접속 정보
mysql_host = "t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com"
mysql_user = "admin"
mysql_password = "dltkddn1"
mysql_db = "testdb1"

# 현재 파일(techextractimg.py)의 디렉토리 경로를 기준으로 tech_book.json 파일의 경로 계산
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로 가져오기
tech_file_path = os.path.join(current_file_dir, "../tech_book.json")  # 상대 경로 계산

# 기술 스택을 식별하는 함수
def identify_tech_stack(text, tech_keywords):
    identified_tech = {}

    for tech, keywords in tech_keywords.items():
        # 키워드 목록을 하나의 정규 표현식으로 합침
        pattern = r'(?i)(?:' + '|'.join(map(re.escape, keywords)) + r')'
        matches = re.findall(pattern, text)  # 대소문자 구분하지 않음

        # 기술이 등장하면 1, 그렇지 않으면 0
        identified_tech[tech] = 1 if matches else 0

    return identified_tech


# tech_book.json 파일을 읽어서 기술 스택과 키워드를 가져오는 함수
def load_tech_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        tech_keywords = json.load(file)
    return tech_keywords


# MySQL에 기술 스택 저장 함수
def save_to_db(notice_id, tot_tech):
    connection = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db,
        charset='utf8mb4'
    )
    try:
        with connection.cursor() as cursor:
            # INSERT 쿼리 작성 (res_tech, qual_tech, pref_tech은 NULL)
            query = """
                INSERT INTO extract_tech_stack (notice_id, tot_tech, res_tech, qual_tech, pref_tech)
                VALUES (%s, %s, NULL, NULL, NULL)
            """
            cursor.execute(query, (notice_id, json.dumps(tot_tech)))
            connection.commit()
    finally:
        connection.close()


# MySQL에서 imgtotext 테이블 데이터를 가져오는 함수
def fetch_imagetotext_data():
    connection = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db,
        charset='utf8mb4'
    )
    try:
        with connection.cursor() as cursor:
            # imgtotext 테이블에서 notice_id와 imgtotext를 가져오는 쿼리
            cursor.execute("""
                SELECT notice_id, imgtotext
                FROM imagetotext
                WHERE imgtotext IS NOT NULL
            """)
            rows = cursor.fetchall()
            return rows
    finally:
        connection.close()


# 기술 키워드 불러오기
if not os.path.exists(tech_file_path):
    raise FileNotFoundError(f"File not found: {tech_file_path}")

tech_keywords = load_tech_keywords(tech_file_path)

# imgtotext 데이터 가져오기
rows = fetch_imagetotext_data()

# 기술 스택 추출 및 저장
for row in rows:
    notice_id = row[0]
    imgtotext = row[1]

    # 텍스트에서 기술 스택 추출
    if imgtotext:
        # 텍스트에서 줄 바꿈 문자(\n, \r)를 제거하고 한 줄로 만들기
        re_text = re.sub(r'[\r\n]+', ' ', imgtotext).strip()

        # 공백 처리만 하고 특수문자는 그대로 유지
        cleaned_text = re.sub(r'\s+', ' ', re_text).strip()

        # 기술 스택 식별
        identified_tech = identify_tech_stack(cleaned_text, tech_keywords)

        # tot_tech 추출
        tot_tech = identified_tech  # 여기서 tot_tech만 사용

        # DB에 저장
        save_to_db(notice_id, tot_tech)
        print(f"Saved notice_id {notice_id} with tot_tech to database.")
