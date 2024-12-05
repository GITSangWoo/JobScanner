import re
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def log_error(error_message):
    """오류를 makelog_err.log 파일에 기록"""
    with open('makelog_err.log', 'a', encoding='utf-8') as err_file:
        timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        err_file.write(f"{timestamp},{error_message}\n")

# 검색 URL 리스트 설정
job_url_list = {
    "DE": [
        "https://jumpit.saramin.co.kr/search?sort=relation&keyword=데이터%20엔지니어"
    ],
    "FE": [
        "https://jumpit.saramin.co.kr/search?sort=relation&keyword=프론트%20엔지니어"
    ],
    "BE": [
        "https://jumpit.saramin.co.kr/search?sort=relation&keyword=백엔드%20엔지니어"
    ],
    "DA": [
        "https://jumpit.saramin.co.kr/search?sort=relation&keyword=데이터%20분석가"
    ],
    "MLE": [
        "https://jumpit.saramin.co.kr/search?sort=relation&keyword=머신러닝%20엔지니어"
    ]
}

# 셀레니움 웹 드라이버 설정
options = Options()
options.headless = False  # 드라이버를 헤드리스 모드로 실행할 수 있음
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 오늘 날짜로 로그 파일 이름 설정
today = datetime.today().strftime('%Y%m%d')

# 로그 파일을 찾을 디렉토리 설정
log_directory = 'jumpit'  # 현재 디렉토리
today_log_file_name = os.path.join(log_directory,f"{today}.log")

# 디렉토리가 존재하는지 확인하고, 없으면 생성
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
    print(f"{log_directory} 디렉토리가 없어서 새로 생성되었습니다.")
else:
    print(f"{log_directory} 디렉토리가 이미 존재합니다.")

log_files = [f for f in os.listdir(log_directory) if re.match(r'^\d{8}\.log$', f)]

# 가장 최근에 생성된 로그 파일 찾기
recent_log_file_name = None  # 기본값을 None으로 설정
if log_files:
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    recent_log_file_name = log_files[0]  # 가장 최근의 로그 파일을 선택
    print(f"Found the most recent log file: {recent_log_file_name}")
else:
    print("No log files found in the directory. All URLs will be marked as 'update'.")

# 이전 로그 파일이 없으면 빈 딕셔너리로 설정 (오늘 크롤링한 URL과 비교할 기준이 없으므로)
previous_urls = {}

# 오늘 크롤링한 URL과 비교하여 상태 설정
for job_key, urls in job_url_list.items():
    for url in urls:
        # 페이지 열기
        driver.get(url)

        # 페이지 로딩 대기: 페이지가 완전히 로드될 때까지 기다리기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        # 스크롤 내리기 및 링크 추출 반복
        previous_height = driver.execute_script("return document.body.scrollHeight")  # 현재 페이지의 높이를 가져옴

        # 페이지가 끝까지 스크롤될 때까지 반복
        while True:
            # 페이지에서 모든 <a> 태그를 찾음
            links = driver.find_elements(By.TAG_NAME, "a")

            # 링크를 모두 추가 (중복 확인은 데이터베이스에서 처리)
            for link in links:
                href = link.get_attribute("href")
                # 정규 표현식으로 'position/숫자' 형식의 링크만 필터링
                if href and re.search(r'position/\d+$', href):
                    # D-day 정보 추출
                    d_day = None  # 기본값을 None으로 설정
                    try:
                        # D-day 정보를 담고 있는 요소를 찾기
                        d_day_elements = link.find_elements(By.XPATH, ".//div[contains(@class, 'sc-d609d44f-3')]/span")
                        if d_day_elements:
                            d_day_text = d_day_elements[0].text.strip()
                            print(f"D-day Text: {d_day_text}")  # D-day 추출된 값 확인
                            if "상시" in d_day_text:
                                d_day = None  # 상시는 null로 저장
                            elif d_day_text.startswith("D-"):
                                d_day = int(d_day_text[2:])  # D-숫자에서 숫자만 추출
                            else:
                                d_day = None
                    except Exception as e:
                        print(f"D-day 추출 실패: {e}")

                    # 로그에 바로 기록
                    job = job_key
                    notice_status = "update"
                    work_status = "null"
                    done_time = "null"
                    print(f"링크: {href}, D-day: {d_day}")  # D-day 값도 함께 출력
                    with open(today_log_file_name, 'a', encoding='utf-8') as file:
                        file.write(f"{job},{href},{notice_status},{work_status},{done_time},{d_day if d_day is not None else 'null'}\n")

            # 스크롤을 페이지 끝까지 내리기
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 잠시 대기하여 새로운 요소들이 로드될 시간을 줌
            time.sleep(2)  # 2초간 대기, 이 시간은 페이지 로딩 속도에 맞게 조절

            # 새로운 페이지 높이가 이전과 같다면 스크롤을 더 이상 내릴 필요가 없으므로 종료
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == previous_height:
                break  # 더 이상 새로운 요소가 로드되지 않으면 반복 종료

            previous_height = new_height  # 이전 높이를 업데이트

        print(f"{job_key} 직무 크롤링 완료")

print("크롤링이 완료되었으며 로그 파일에 실시간으로 저장되었습니다.")
driver.quit()
