import pymysql
import re
import json
import os

# RDS MySQL 접속 정보
mysql_host = "t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com"
mysql_user = "admin"  # RDS 생성 시 설정한 사용자 이름
mysql_password = "dltkddn1"  # 비밀번호
mysql_db = "testdb1"  # 사용하려는 데이터베이스 이름


# MySQL에서 qualification, responsibility, preferential 컬럼 데이터를 가져오는 함수
def fetch_data():
    connection = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db,
        charset='utf8mb4'
    )
    try:
        with connection.cursor() as cursor:
            # qualification, responsibility, preferential 컬럼 값과 id를 가져오는 쿼리
            cursor.execute("""
                SELECT id, qualification, responsibility, preferential
                FROM combined_table
                WHERE qualification IS NOT NULL OR responsibility IS NOT NULL OR preferential IS NOT NULL
            """)
            rows = cursor.fetchall()
            return rows
    finally:
        connection.close()


# tech_book.json 파일 경로를 스크립트 위치 기준으로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 스크립트의 디렉토리 경로
tech_file_path = os.path.join(script_dir, '../tech_book.json')  # 상대 경로로 tech_book.json 설정


# tech_book.json 파일을 읽어서 기술 스택과 키워드를 가져오는 함수
def load_tech_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        tech_keywords = json.load(file)
    return tech_keywords


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


# 텍스트에서 불필요한 공백을 제거하는 함수
def clean_text(text):
    # 여러 공백을 하나의 공백으로 바꿔줌
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    return cleaned_text


# MySQL에 기술 스택 저장 함수
def save_to_db(notice_id, tot_tech, res_tech, qual_tech, pref_tech):
    connection = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db,
        charset='utf8mb4'
    )
    try:
        with connection.cursor() as cursor:
            # INSERT 쿼리 작성
            query = """
                INSERT INTO extract_tech_stack (notice_id, tot_tech, res_tech, qual_tech, pref_tech)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (notice_id, json.dumps(tot_tech), json.dumps(res_tech), json.dumps(qual_tech), json.dumps(pref_tech)))
            connection.commit()
    finally:
        connection.close()


# 기술 키워드 불러오기
tech_keywords = load_tech_keywords(tech_file_path)
rows = fetch_data()

# 공고별 기술 스택 추출 및 저장
for row in rows:
    notice_id = row[0]  # 첫 번째 값은 공고 ID
    tot_tech = {}
    res_tech = {}
    qual_tech = {}
    pref_tech = {}

    # 중복 확인 로직 추가
    connection = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db,
        charset='utf8mb4'
    )
    try:
        with connection.cursor() as cursor:
            # 중복 확인 쿼리
            check_query = """
                SELECT COUNT(*)
                FROM extract_tech_stack
                WHERE notice_id = %s
            """
            cursor.execute(check_query, (notice_id,))
            exists = cursor.fetchone()[0]

            # 중복이면 스킵
            if exists:
                print(f"Notice ID {notice_id} already exists. Skipping...")
                continue  # 다음 row로 넘어감
    finally:
        connection.close()

    # 각 컬럼에 대해 기술 스택을 식별
    for col_index, col_name in enumerate(["responsibility", "qualification", "preferential"]):
        text = row[col_index + 1]  # 첫 번째 값은 ID이므로 두 번째 값부터 시작

        if text:  # 텍스트가 존재하는 경우만 처리
            # 텍스트에서 줄 바꿈 문자(\n, \r)를 제거하고 한 줄로 만들기
            re_text = re.sub(r'[\r\n]+', ' ', text).strip()

            # 공백 처리만 하고 특수문자는 그대로 유지
            cleaned_text = clean_text(re_text)

            # 기술 스택 식별
            identified_tech = identify_tech_stack(cleaned_text, tech_keywords)

            # 각 컬럼에 대한 기술 스택 저장
            if col_name == "responsibility":
                res_tech = identified_tech
            elif col_name == "qualification":
                qual_tech = identified_tech
            elif col_name == "preferential":
                pref_tech = identified_tech

            # 전체 기술 스택을 tot_tech에 합침 (중복된 기술 스택은 1로 표시)
            for tech, value in identified_tech.items():
                if tech not in tot_tech:
                    tot_tech[tech] = value
                else:
                    tot_tech[tech] = max(tot_tech[tech], value)

    # DB에 저장
    save_to_db(notice_id, tot_tech, res_tech, qual_tech, pref_tech)
    print(f"Saved notice_id {notice_id} to database.")
