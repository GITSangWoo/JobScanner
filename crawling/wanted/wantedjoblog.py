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
  
  
if not os.path.exists('./wanted'):
        os.makedirs('./wanted')  # 디렉토리 생성  
  
def log_error(error_message):
    """오류를 makelog_err.log 파일에 기록"""
    # ./wanted 디렉토리가 없으면 생성
    with open('./wanted/makelog_err.log', 'a', encoding='utf-8') as err_file:
        timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        err_file.write(f"{timestamp},{error_message}\n")

job_url_list = {
    "DE": [
        "https://www.wanted.co.kr/search?query=데이터+엔지니어&tab=position",
    ],
    "FE": [
        "https://www.wanted.co.kr/search?query=프론트엔드&tab=position"
    ],
    "BE": [
        "https://www.wanted.co.kr/search?query=백엔드&tab=position"
    ],
    "DA": [
        "https://www.wanted.co.kr/search?query=데이터+분석가&tab=position",
    ],
    "MLE": [
        "https://www.wanted.co.kr/search?query=머신러닝+엔지니어&tab=position",
    ]
}

try:
    # 셀레니움 웹 드라이버 설정
    options = Options()
    options.headless = False  # 드라이버를 헤드리스 모드로 실행할 수 있음 (주석 처리하거나 True로 설정하여 브라우저를 표시하지 않게 할 수 있음)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 오늘 날짜로 로그 파일 이름 설정
    today = datetime.today().strftime('%Y%m%d')
    today_log_file_name = f"./wanted/{today}.log"

    # 로그 파일을 찾을 디렉토리 설정
    log_directory = './wanted'  # 원하는 디렉토리로 변경
    log_files = [f for f in os.listdir(log_directory) if re.match(r'^\d{8}\.log$', f)]

    # 가장 최근에 생성된 로그 파일 찾기
    if log_files:
        # 파일들을 생성 시간 기준으로 정렬하고 가장 최근 파일을 선택
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_directory, x)), reverse=True)
        recent_log_file_name = log_files[0]  # 가장 최근의 로그 파일을 선택
        print(f"Found the most recent log file: {recent_log_file_name}")
    else:
        print("No log files found in the directory. All URLs will be marked as 'update'.")

    # 이전 로그 파일이 존재하는지 확인하고 읽기
    previous_urls = {}  # 이전 로그에 있는 URL 및 해당 job
    if os.path.exists(os.path.join(log_directory, recent_log_file_name)):
        with open(os.path.join(log_directory, recent_log_file_name), 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:  # 파일에 내용이 있을 때만 처리
                for line in lines[1:]:  # 첫 번째 줄은 header
                    columns = line.strip().split(',')
                    if len(columns) >= 5:  # 만약 각 열이 다 있다면
                        url = columns[1]
                        job = columns[0]  # 해당 URL의 job
                        notice_status = columns[2]
                        if notice_status != "deleted":  # "deleted" 상태인 URL은 제외
                            previous_urls[url] = job  # URL에 해당하는 job을 저장

    # 오늘 크롤링한 URL을 수집
    all_links = []  # 오늘 수집한 모든 링크
    job_for_links = {}  # 각 링크에 해당하는 job을 기록하기 위한 dictionary

    # 각 job (키값)에 대한 URL 처리
    for job_key, urls in job_url_list.items():
        for url in urls:
            # 페이지 열기
            driver.get(url)

            # 페이지 로딩 대기: 페이지가 완전히 로드될 때까지 기다기
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )

            # 정규 표현식 패턴 (wd/ 뒤에 숫자가 있는 URL을 찾는 패턴)
            pattern = re.compile(r'wd/\d+$')

            # 스크롤 내리기 및 링크 추출 반복
            previous_height = driver.execute_script("return document.body.scrollHeight")  # 현재 페이지의 높이를 가져옴

            while True:
                # 페이지에서 모든 <a> 태그를 찾음
                links = driver.find_elements(By.TAG_NAME, "a")

                # 이미 가져온 링크들을 확인하고 중복되지 않게 추가
                for link in links:
                    href = link.get_attribute("href")
                    # 정규 표현식으로 'wd/숫자' 형식의 링크만 필터링
                    if href and pattern.search(href) and href not in all_links:
                        all_links.append(href)
                        job_for_links[href] = job_key  # 링크에 해당하는 job 기록

                # 스크롤을 페이지 끝까지 내리기
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # 잠시 대기하여 새로운 요소들이 로드될 시간을 줌
                time.sleep(2)  # 2초간 대기, 이 시간은 페이지 로딩 속도에 맞게 조절

                # 새로운 페이지 높이가 이전과 같다면 스크롤을 더 이상 내릴 필요가 없으므로 종료
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == previous_height:
                    break  # 더 이상 새로운 요소가 로드되지 않으면 반복 종료

                previous_height = new_height  # 이전 높이를 업데이트

    # 오늘 크롤링한 URL을 기준으로 상태를 설정
    log_data_deleted = []  # deleted 상태를 따로 저장
    log_data_other = []    # 나머지 (exist, update) 상태를 따로 저장

    # 오늘 크롤링한 링크와 이전 로그의 비교
    all_urls_set = set(all_links)
    previous_urls_set = set(previous_urls.keys())

    # 1. 존재하는 링크 처리 (오늘만 존재)
    existing_urls = all_urls_set & previous_urls_set  # 오늘과 어제 모두 존재하는 링크
    for url in existing_urls:
        notice_status = "exist"
        work_status = "done"  # 상태는 'done'으로 설정
        done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        job = job_for_links.get(url, 'unknown')  # 해당 URL의 job을 가져옴
        log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    # 2. 새로 추가된 링크 처리 (오늘만 있는 링크)
    new_urls = all_urls_set - previous_urls_set  # 오늘만 존재하는 링크
    for url in new_urls:
        notice_status = "update"
        work_status = "null"
        done_time = "null"
        job = job_for_links[url]  # 새 URL에는 해당 job_key 값을 사용
        log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    # 3. 삭제된 링크 처리 (어제 있었으나 오늘은 없는 링크)
    deleted_urls = previous_urls_set - all_urls_set  # 어제는 있었지만 오늘은 없는 것
    for url in deleted_urls:
        notice_status = "deleted"
        work_status = "done"
        done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 삭제된 시간을 현재 시간으로 설정
        # 이전 로그에서 해당 URL의 job을 가져옴
        job = previous_urls.get(url, 'unknown')  # 어제의 job 값을 사용
        log_data_deleted.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    # 로그 파일 저장
    with open(today_log_file_name, 'w', encoding='utf-8') as file:
        # 헤더 작성
        file.write("job,url,notice_status,work_status,done_time\n")
        # deleted 항목을 먼저 기록
        for line in log_data_deleted:
            file.write(line + "\n")
        # 나머지 (exist, update) 항목을 그 뒤에 기록
        for line in log_data_other:
            file.write(line + "\n")

    # 브라우저 종료
    driver.quit()

except Exception as e:
    # 오류 발생 시 오류 메시지 기록
    error_message = str(e)
    log_error(error_message)
    # 프로그램 종료 전 브라우저 종료
    if 'driver' in locals():
        driver.quit()

