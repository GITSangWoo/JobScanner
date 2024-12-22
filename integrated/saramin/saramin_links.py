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
from urllib.parse import unquote

if not os.path.exists('./saramin'):
    os.makedirs('./saramin')  # 디렉토리 생성

def log_error(error_message):
    """오류를 날짜별로 makelog_err_YYYYMMDD.log 파일에 기록"""
    today = datetime.today().strftime('%Y%m%d')  # 날짜 포맷
    log_filename = f'./saramin/makelog_err_{today}.log'  # 파일명에 날짜 추가
    with open(log_filename, 'a', encoding='utf-8') as err_file:
        timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        err_file.write(f"{timestamp},{error_message}\n")

def log_process(process_message):
    """프로세스 로그를 날짜별로 makelog_process_YYYYMMDD.log 파일에 기록"""
    today = datetime.today().strftime('%Y%m%d')  # 날짜 포맷
    log_filename = f'./saramin/makelog_process_{today}.log'  # 파일명에 날짜 추가
    with open(log_filename, 'a', encoding='utf-8') as process_file:
        timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        process_file.write(f"{timestamp},{process_message}\n")

def convert_html_entities_to_url(html_link):
    """HTML 엔티티를 URL로 변환하고, 상대경로를 절대경로로 변환"""
    # HTML 엔티티 &amp;를 &로 변환
    html_link = html_link.replace('&amp;', '&')

    # 상대 경로에 도메인 추가
    base_url = "https://www.saramin.co.kr"
    if html_link.startswith('/'):
        html_link = base_url + html_link

    # URL 인코딩된 값 복원 (예: %2F -> /)
    html_link = unquote(html_link)

    return html_link

def has_uuid(url):
    """URL에 uuid가 포함되어 있는지 확인"""
    return bool(re.search(r'[0-9a-fA-F-]{36}', url))  # UUID 형식을 정규표현식으로 검사

# 글로벌 변수 선언
job_url_list = {
    "DE": [
        "https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchType=recently&searchword=데이터%20엔지니어&recruitPage={}&recruitSort=relation&recruitPageCount=40&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&show_applied=&quick_apply=&except_read=&ai_head_hunting=&mainSearch=n",
    ],
    "FE": [
        "https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&keydownAccess=&searchword=프론트엔드&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={}&recruitSort=relation&recruitPageCount=40&inner_com_type=&show_applied=&quick_apply=&except_read=&ai_head_hunting=",
    ],
    "BE": [
        "https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&keydownAccess=&searchword=백엔드&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={}&recruitSort=relation&recruitPageCount=40&inner_com_type=&show_applied=&quick_apply=&except_read=&ai_head_hunting=",
    ],
    "MLE": [
        "https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&keydownAccess=&searchword=머신러닝%20엔지니어&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={}&recruitSort=relation&recruitPageCount=40&inner_com_type=&show_applied=&quick_apply=&except_read=&ai_head_hunting=",
    ],
    "DA": [
        "https://www.saramin.co.kr/zf_user/search/recruit?searchType=search&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&keydownAccess=&searchword=데이터%20분석가&panel_type=&search_optional_item=y&search_done=y&panel_count=y&preview=y&recruitPage={}&recruitSort=relation&recruitPageCount=40&inner_com_type=&show_applied=&quick_apply=&except_read=&ai_head_hunting=",
    ]
}

try:
    # 셀레니움 웹 드라이버 설정
    options = Options()
    options.headless = False  # 드라이버를 헤드리스 모드로 실행할 수 있음 (True로 설정하여 브라우저를 표시하지 않게 할 수 있음)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    log_process("Chrome WebDriver started.")

    # 오늘 날짜로 로그 파일 이름 설정
    today = datetime.today().strftime('%Y%m%d')
    today_log_file_name = f"./saramin/{today}.log"

    # 로그 파일을 찾을 디렉토리 설정
    log_directory = './saramin'  # 원하는 디렉토리로 변경
    log_files = [f for f in os.listdir(log_directory) if re.match(r'^\d{8}\.log$', f)]

    # 가장 최근에 생성된 로그 파일 찾기
    if log_files:
        log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_directory, x)), reverse=True)
        recent_log_file_name = log_files[0]  # 가장 최근의 로그 파일을 선택
        log_process(f"Found the most recent log file: {recent_log_file_name}")
    else:
        log_process("No log files found in the directory. All URLs will be marked as 'update'.")
        recent_log_file_name = None  # recent_log_file_name을 None으로 설정

    # 이전 로그 파일이 존재하는지 확인하고 읽기
    previous_urls = {}  # 이전 로그에 있는 URL 및 해당 job
    if recent_log_file_name and os.path.exists(os.path.join(log_directory, recent_log_file_name)):
        with open(os.path.join(log_directory, recent_log_file_name), 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if lines:  # 파일에 내용이 있을 때만 처리
                for line in lines[1:]:  # 첫 번째 줄은 header
                    columns = line.strip().split(',')
                    if len(columns) >= 5:  # 만약 각 열이 다 있다면
                        url = columns[1]
                        job = columns[0]  # 해당 URL의 job
                        notice_status = columns[2]
                        work_status = columns[3]
                        done_time = columns[4]
                        if notice_status != "deleted":  # "deleted" 상태인 URL은 제외
                            previous_urls[url] = {'job': job, 'notice_status': notice_status, 'work_status': work_status, 'done_time': done_time}  # URL에 해당하는 정보 저장

    # 오늘 크롤링한 URL을 수집
    all_links = []  # 오늘 수집한 모든 링크
    job_for_links = {}  # 각 링크에 해당하는 job을 기록하기 위한 dictionary

    # 각 job (키값)에 대한 URL 처리
    for job_key, urls in job_url_list.items():
        for url in urls:
            log_process(f"Processing job: {job_key}, URL: {url}")
            for page_number in range(1, 41):  # 1부터 40까지 페이지 크롤링
                page_url = url.format(page_number)
                driver.get(page_url)

                # 페이지 로딩 대기
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "a")))

                # 링크 추출
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        converted_url = convert_html_entities_to_url(href)

                        # UUID가 포함된 링크만 추가
                        if has_uuid(converted_url) and converted_url not in all_links:
                            all_links.append(converted_url)
                            job_for_links[converted_url] = job_key  # 링크와 job 정보를 매핑

    # 크롤링 완료 후, 링크 정보를 로그로 기록
    for link in all_links:
        job = job_for_links[link]
        log_process(f"{job}, {link}")

    # 오늘 크롤링한 URL과 이전 로그 파일을 비교하여 상태 설정
    log_data_deleted = []  # deleted 상태를 따로 저장
    log_data_other = []    # 나머지 (exist, update) 상태를 따로 저장

    # 1. 오늘 크롤링한 URL과 이전 로그 파일의 비교
    for url in all_links:
        if url in previous_urls:
            # 이전 로그 파일과 오늘 모두 존재하는 URL이면 "exist"로 처리
            if previous_urls[url]['notice_status'] == "deleted":
                continue
            notice_status = "exist"
            work_status = previous_urls[url]['work_status']
            done_time = previous_urls[url]['done_time']
            job = previous_urls[url]['job']
            log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")
        else:
            # 오늘만 존재하는 URL은 "update"로 설정
            notice_status = "update"
            work_status = "null"
            done_time = "null"
            job = job_for_links[url]
            log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    # 2. 이전 로그 파일에 있지만 오늘 로그 파일에 없는 URL 처리
    for url in previous_urls:
        if url not in all_links:
            notice_status = "deleted"
            work_status = "done"
            done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            job = previous_urls[url]['job']
            log_data_deleted.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    # 로그 파일 저장
    with open(today_log_file_name, 'w', encoding='utf-8') as file:
        file.write("job,url,notice_status,work_status,done_time\n")
        for line in log_data_deleted:
            file.write(line + "\n")
        for line in log_data_other:
            file.write(line + "\n")

    log_process(f"Log file saved: {today_log_file_name}")

except Exception as e:
    # 오류 발생 시 오류 메시지 기록
    error_message = str(e)
    log_error(error_message)
    log_process(f"Error occurred: {error_message}")
    if 'driver' in locals():
        driver.quit()
        log_process("Chrome WebDriver closed after error.")

finally:
    # 드라이버 종료 (예외 없이 처리되었을 경우에도)
    if 'driver' in locals():
        driver.quit()
        log_process("Chrome WebDriver closed.")   

# saramin done 
