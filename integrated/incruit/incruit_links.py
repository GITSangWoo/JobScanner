import os
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# incruit 디렉토리 확인 및 생성
if not os.path.exists('./incruit'):
    os.makedirs('./incruit')  # 디렉토리 생성

def log_error(error_message):
    """오류를 incruit/makelog_err_YYYYMMDD.log 파일에 기록"""
    today = datetime.today().strftime('%Y%m%d')
    log_file_name = f'./incruit/makelog_err_{today}.log'
    with open(log_file_name, 'a', encoding='utf-8') as err_file:
        timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        err_file.write(f"{timestamp},{error_message}\n")

def log_process(message):
    """프로세스 상태를 incruit/makelog_process_YYYYMMDD.log 파일에 기록하고 화면에 출력"""
    today = datetime.today().strftime('%Y%m%d')
    log_file_name = f'./incruit/makelog_process_{today}.log'
    print(message)
    with open(log_file_name, 'a', encoding='utf-8') as process_file:
        timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        process_file.write(f"{timestamp},{message}\n")

job_url_list = {
    "DE": [
        "https://search.incruit.com/list/search.asp?col=job&kw=%B5%A5%C0%CC%C5%CD+%BF%A3%C1%F6%B4%CF%BE%EE&startno={}"
    ],
    "FE": [
        "https://search.incruit.com/list/search.asp?col=job&kw=%C7%C1%B7%D0%C6%AE&startno={}"
    ],
    "BE": [
        "https://search.incruit.com/list/search.asp?col=job&kw=%B9%E9%BF%A3%B5%E5&startno={}"
    ],
    "DA": [
        "https://search.incruit.com/list/search.asp?col=job&kw=%B5%A5%C0%CC%C5%CD+%BA%D0%BC%AE%B0%A1&startno={}"
    ],
    "MLE": [
        "https://search.incruit.com/list/search.asp?col=job&kw=%B8%D3%BD%C5%B7%AF%B4%D7+%BF%A3%C1%F6%B4%CF%BE%EE&startno={}"
    ]
}

try:
    # 오늘 날짜로 로그 파일 이름 설정
    today = datetime.today().strftime('%Y%m%d')
    today_log_file_name = f"./incruit/{today}.log"

    # 로그 파일을 찾을 디렉토리 설정
    log_directory = './incruit'
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
            if lines:
                log_process(f"Reading existing log file: {recent_log_file_name}")
                for line in lines[1:]:  # 첫 번째 줄은 header
                    columns = line.strip().split(',')
                    if len(columns) >= 5:
                        url = columns[1]
                        job = columns[0]  # 해당 URL의 job
                        notice_status = columns[2]
                        if notice_status != "deleted":  # "deleted" 상태인 URL은 제외
                            previous_urls[url] = {
                                'job': job,
                                'notice_status': notice_status,
                                'work_status': columns[3],
                                'done_time': columns[4]
                            }
    else:
        log_process("No previous log file to read or file is empty.")

    # 오늘 크롤링한 URL을 수집
    all_links = []  # 오늘 수집한 모든 링크
    job_for_links = {}  # 각 링크에 해당하는 job을 기록하기 위한 dictionary

    # 각 job (키값)에 대한 URL 처리
    for job_key, urls in job_url_list.items():
        for url in urls:
            start_page = 0
            end_page = 38
            page_step = 30  # 페이지네이션의 startno는 30씩 증가

            # 페이지 순차적으로 크롤링
            for page in range(start_page, end_page):
                startno = page * page_step
                formatted_url = url.format(startno)

                log_process(f"Fetching URL: {formatted_url} (page {page})")
                # HTTP 요청 보내기
                response = requests.get(formatted_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 직무 공고 링크 추출 (jobdb_info 클래스에 포함된 a 태그)
                job_links_on_page = soup.find_all('a', href=True)

                for link_tag in job_links_on_page:
                    link = link_tag['href']
                    if "jobdb_info" in link:
                        full_link = "https://www.incruit.com" + link if link.startswith('/') else link
                        if full_link not in all_links:
                            all_links.append(full_link)
                            job_for_links[full_link] = job_key  # 링크에 해당하는 job 기록

    log_process("Crawling completed. Now processing URLs.")

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
        work_status = previous_urls[url]['work_status']  # 이전의 상태 그대로
        done_time = previous_urls[url]['done_time']  # 이전의 done_time 그대로
        job = previous_urls[url]['job']  # 이전 로그에서 job 값 가져오기
        log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    log_process(f"Processed {len(existing_urls)} existing URLs.")

    # 2. 새로 추가된 링크 처리 (오늘만 있는 링크)
    new_urls = all_urls_set - previous_urls_set  # 오늘만 존재하는 링크
    for url in new_urls:
        notice_status = "update"
        work_status = "null"
        done_time = "null"
        job = job_for_links[url]  # 새 URL에는 해당 job_key 값을 사용
        log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    log_process(f"Processed {len(new_urls)} new URLs.")

    # 3. 삭제된 링크 처리 (어제 있었으나 오늘은 없는 링크)
    deleted_urls = previous_urls_set - all_urls_set  # 어제는 있었지만 오늘은 없는 것
    for url in deleted_urls:
        notice_status = "deleted"
        work_status = "done"
        done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 삭제된 시간을 현재 시간으로 설정
        job = previous_urls[url]['job']  # 이전 로그에서 job 값 가져오기
        log_data_deleted.append(f"{job},{url},{notice_status},{work_status},{done_time}")

    log_process(f"Processed {len(deleted_urls)} deleted URLs.")

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

    log_process(f"Log file '{today_log_file_name}' has been written successfully.")

except Exception as e:
    # 오류 발생 시 오류 메시지 기록
    error_message = str(e)
    log_error(error_message)
    log_process(f"An error occurred: {error_message}")  
    
    
 # incruit url 크롤링 완성    
