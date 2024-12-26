import os
import json
import mysql.connector

# MySQL 연결
conn = mysql.connector.connect(
    host="t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com",
    user="admin",
    password="dltkddn1",
    database="service"
)
cursor = conn.cursor()

# 현재 파일(add_tech.py)의 디렉토리 경로를 기준으로 상대 경로 계산
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로 가져오기
json_file_path = os.path.join(current_file_dir, "../../../tech/tech_book.json")  # 상대 경로 계산

# JSON 파일 로드
try:
    with open(json_file_path, "r", encoding="utf-8") as file:
        tech_data = json.load(file)
except FileNotFoundError:
    print(f"JSON 파일을 찾을 수 없습니다: {json_file_path}")
    tech_data = {}

# 기술 스택 리스트 추출
tech_stack_list = list(tech_data.keys())

# base_link 정의
base_link = "https://www.aladin.co.kr/search/wsearchresult.aspx?SearchTarget=Book&KeyWord={tech_name}&KeyRecentPublish=0&CategorySearch=%EC%BB%B4%ED%93%A8%ED%84%B0%2F%EB%AA%A8%EB%B0%94%EC%9D%BC%40351&OutStock=0&ViewType=Detail&SortOrder=2&CustReviewCount=0&CustReviewRank=0&KeyFullWord={tech_name}&KeyLastWord={tech_name}&chkKeyTitle=&chkKeyAuthor=&chkKeyPublisher=&chkKeyISBN=&chkKeyTag=&chkKeyTOC=&chkKeySubject=&ViewRowCount=25&SuggestKeyWord="

# SQL 업데이트 쿼리
update_query = """
UPDATE tech_stack
SET book_link = %s
WHERE tech_name = %s
"""

# 데이터베이스 업데이트 및 성공 카운트 초기화
success_count = 0  # 성공적으로 업데이트된 항목 수를 저장할 변수

for tech_name in tech_stack_list:
    # C나 Go인 경우 "언어"를 붙임
    if tech_name in ["C", "GO"]:
        book_link = base_link.replace("{tech_name}", f"{tech_name} 언어")
    else:
        # 일반 기술 이름 처리
        book_link = base_link.replace("{tech_name}", tech_name)
    
    try:
        # 데이터베이스 업데이트 실행
        cursor.execute(update_query, (book_link, tech_name))
        success_count += 1  # 성공적으로 업데이트된 경우 카운트 증가
    except mysql.connector.Error as err:
        print(f"Error updating {tech_name}: {err}")

# 변경 사항 커밋 및 연결 종료
conn.commit()
cursor.close()
conn.close()

# 성공적으로 삽입된 항목 수 출력
print(f"총 {success_count}개의 기술 스택에 book_link가 삽입되었습니다.")
