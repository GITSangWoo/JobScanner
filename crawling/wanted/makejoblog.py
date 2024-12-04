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


job_url_list = {
    "DE": [
        "https://www.wanted.co.kr/search?query=데이터+엔지니어&tab=position",
        "https://www.wanted.co.kr/search?query=데이터엔지니어&tab=position"
    ],
    "FE": [
        "https://www.wanted.co.kr/search?query=프론트+엔지니어&tab=position",
        "https://www.wanted.co.kr/search?query=프론트엔지니어&tab=position"
    ],
    "BE": [
        "https://www.wanted.co.kr/search?query=백엔드+엔지니어&tab=position",
        "https://www.wanted.co.kr/search?query=백엔드엔지니어&tab=position"
    ],
    "DA": [
        "https://www.wanted.co.kr/search?query=데이터+분석가&tab=position",
        "https://www.wanted.co.kr/search?query=데이터분석가&tab=position"
    ],
    "MLE": [
        "https://www.wanted.co.kr/search?query=머신러닝+엔지니어&tab=position",
        "https://www.wanted.co.kr/search?query=머신러닝엔지니어&tab=position"
    ]
}

try:
    # 셀레니움 웹 드라이버 설정
    options = Options()
    options.headless = False  # 드라이버를 헤드리스 모드로 실행할 수 있음 (주석 처리하거나 True로 설정하여 브라우저를 표시하지 않게 할 수 있음)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 오늘 날짜로 로그 파일 이름 설정
    today = datetime.today().strftime('%Y%m%d')
    today_log_file_name = f"{today}.log"

    # 로그 파일을 찾을 디렉토리 설정
    log_directory = '.'  # 현재 디렉토리
    log_files = [f for f in os.listdir(log_directory) if re.match(r'^\d{8}\.log$', f)]

    # 가장 최근에 생성된 로그 파일 찾기
    if log_files:
        # 파일들을 생성 시간 기준으로 정렬하고 가장 최근 파일을 선택
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        recent_log_file_name = log_files[0]  # 가장 최근의 로그 파일을 선택
        print(f"Found the most recent log file: {recent_log_file_name}")
    else:
        print("No log files found in the directory. All URLs will be marked as 'update'.")

    # 이전 로그 파일이 존재하는지 확인하고 읽기
    previous_urls = {}
    if os.path.exists(recent_log_file_name):
        with open(recent_log_file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:  # 파일에 내용이 있을 때만 처리
                for line in lines[1:]:  # 첫 번째 줄은 header
                    columns = line.strip().split(',')
                    if len(columns) >= 5:  # 만약 각 열이 다 있다면
                        url = columns[1]
                        notice_status = columns[2]
                        work_status = columns[3]
                        done_time = columns[4]
                        job = columns[0]  # 이전 로그에서 job을 가져옴
                        previous_urls[url] = {
                            'job': job,  # 이전 로그에서 job 값도 함께 저장
                            'notice_status': notice_status,
                            'work_status': work_status,
                            'done_time': done_time
                        }
            else:
                print("The log file is empty.")

    # 오늘 로그 파일에 기록할 내용 생성
    log_data_deleted = []  # deleted 상태를 따로 저장
    log_data_other = []    # 나머지 (exist, update) 상태를 따로 저장

    # 모든 링크를 먼저 수집
    all_links = []
    job_for_links = {}  # 각 링크에 해당하는 job을 기록하기 위한 dictionary

    # 각 job (키값)에 대한 URL 처리
    for job_key, urls in job_url_list.items():
        for url in urls:
            # 페이지 열기
            driver.get(url)

            # 페이지 로딩 대기: 페이지가 완전히 로드될 때까지 기다리기
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

    # 오늘 크롤링한 URL과 최근 로그 파일을 비교하여 상태 설정
    for url in all_links:
        if url in previous_urls:
            # 이전 로그 파일과 오늘 모두 존재하는 URL이면 "exist"로 처리
            if previous_urls[url]['notice_status'] == "deleted":
                # 이미 'deleted' 상태로 존재하는 공고는 다시 "deleted"로 처리하지 않음
                continue
            notice_status = "exist"
            work_status = previous_urls[url]['work_status']  # 이전의 상태 그대로
            done_time = previous_urls[url]['done_time']  # 이전의 done_time 그대로
            job = previous_urls[url]['job']  # 이전 로그에서 job 값 가져오기
            log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")
        else:
            # 오늘만 존재하는 URL은 "update"로 설정
            notice_status = "update"
            work_status = "null"
            done_time = "null"
            job = job_for_links[url]  # 새 URL에는 해당 job_key 값을 사용
            log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")  # 새 URL에는 해당 job_key 값을 사용

    # 이전 로그 파일에 있지만 오늘 로그 파일에 없는 URL 처리
    for url in previous_urls:
        if url not in all_links:
            # 이전에는 존재했지만 오늘은 없는 URL은 "deleted"로 설정
            if previous_urls[url]['notice_status'] == "deleted":
                # 이미 'deleted' 상태로 기록된 공고는 다시 'deleted'로 갱신하지 않음
                continue
            notice_status = "deleted"
            work_status = "done"
            done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 삭제된 시간을 현재 시간으로 설정
            job = previous_urls[url]['job']  # 이전 로그에서 job 값 가져오기
            log_data_deleted.append(f"{job},{url},{notice_status},{work_status},{done_time}")  # 삭제된 URL은 따로 추가

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

