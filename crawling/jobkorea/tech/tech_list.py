import pymysql
import re
import json

# MySQL 연결 설정
mysql_host = '43.201.40.223'
mysql_user = 'user'
mysql_password = '1234'
mysql_db = 'testdb'

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
                FROM wanted 
                WHERE qualification IS NOT NULL OR responsibility IS NOT NULL OR preferential IS NOT NULL
                LIMIT 10
            """)
            rows = cursor.fetchall()
            return rows
    finally:
        connection.close()

# 기술 관련 키워드를 포함하는 tech_book.json 파일 경로
tech_file_path = 'tech_book.json'

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
        
        if matches:
            identified_tech[tech] = matches  # 기술 및 관련 키워드를 기록
            
    return identified_tech

# 텍스트에서 불필요한 공백을 제거하는 함수
def clean_text(text):
    # 여러 공백을 하나의 공백으로 바꿔줌
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    return cleaned_text

# MySQL에서 가져온 데이터로 기술 스택을 식별하는 함수
def process_data():
    tech_keywords = load_tech_keywords(tech_file_path)
    rows = fetch_data()

    for row in rows:
        print(f"\n[ID] {row[0]}\n")
        print("---------------------------")
        # 각 컬럼에 대해 기술 스택을 식별
        for col_index, col_name in enumerate(["responsibility", "qualification", "preferential"]):
            text = row[col_index + 1]  # 첫 번째 값은 ID이므로, 두 번째 값부터 시작

            if text:  # 텍스트가 존재하는 경우
                # 텍스트에서 줄 바꿈 문자(\n, \r)를 제거하고 한 줄로 만들기
                re_text = re.sub(r'[\r\n]+', ' ', text).strip()

                # 공백 처리만 하고 특수문자는 그대로 유지
                cleaned_text = clean_text(re_text)
                print(f"\n[텍스트]")
                print(f"\n{text}\n")

                # 기술 스택 식별
                identified_tech = identify_tech_stack(cleaned_text, tech_keywords)

                # ID 출력과 함께 기술 스택 결과 출력
                if identified_tech:
                    if col_name == "responsibility":
                        print("\n[주요업무에서 식별된 기술 스택]\n")
                    elif col_name == "qualification":
                        print("\n[자격요건에서 식별된 기술 스택]\n")
                    elif col_name == "preferential":
                        print("\n[우대사항에서 식별된 기술 스택]\n")
                    for key, value in identified_tech.items():
                        print(f"{key}")
                        print(value)
                else:
                    print(f"\n{col_name} 식별된 기술 스택이 없습니다.")
                print("\n---------------------------")
            else:
                print(f"\n{col_name} 데이터가 없습니다.")

# 실제 데이터 처리 실행
process_data()
