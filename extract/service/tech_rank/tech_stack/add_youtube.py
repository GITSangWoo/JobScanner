import os
import json
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 현재 파일(add_tech.py)의 디렉토리 경로를 기준으로 tech_book.json 파일의 경로 계산
current_file_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 절대 경로 가져오기
json_file_path = os.path.join(current_file_dir, "../../../tech/tech_book.json")  # 상대 경로 계산

# tech_book.json 파일에서 키값 읽기
with open(json_file_path, "r", encoding="utf-8") as json_file:
    tech_data = json.load(json_file)
    tech_names = list(tech_data.keys())  # JSON의 키값을 리스트로 변환

# WebDriver 설정 및 초기화
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# MySQL 연결 설정
conn = mysql.connector.connect(
    host="t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com",
    user="admin",
    password="dltkddn1",
    database="service"
)
cursor = conn.cursor()

# SQL 업데이트 쿼리
update_query = """
UPDATE tech_stack
SET youtube_link = %s
WHERE tech_name = %s
"""

try:
    for tech_name in tech_names:
        # Google 검색 URL 생성 (직접 검색 URL 사용)
        search_url = f"https://www.google.com/search?q={tech_name}+사용법+유튜브"
        driver.get(search_url)
        time.sleep(3)  # 페이지 로딩 대기

        # 첫 번째 검색 결과에서 YouTube 링크 추출
        try:
            # <a> 태그에서 href 속성을 가진 YouTube 링크 찾기
            first_result = driver.find_element(By.CSS_SELECTOR, "a[href*='youtube.com/watch']")
            youtube_url = first_result.get_attribute("href")

            if youtube_url:
                # DB에 업데이트 실행
                cursor.execute(update_query, (youtube_url, tech_name))
                print(f"Updated {tech_name} with {youtube_url}")
            else:
                print(f"No valid YouTube link found for {tech_name}")
        except Exception as e:
            print(f"오류 발생 for {tech_name}: {e}")

finally:
    # 브라우저 닫기 및 DB 커밋/연결 종료
    driver.quit()
    conn.commit()
    cursor.close()
    conn.close()

print("DB 업데이트가 완료되었습니다.")
