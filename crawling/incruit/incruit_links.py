import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
from collections import defaultdict

# 검색 URL 리스트 설정
job_url_list = {
    "DE": [
        #"https://search.incruit.com/list/search.asp?col=all&src=gsw*www&kw=데이터+엔지니어"
        "https://search.incruit.com/list/search.asp?col=job&kw=데이터+엔지니어&startno={}"
    ],
    "FE": [
        #"https://search.incruit.com/list/search.asp?col=all&src=gsw*www&kw=프론트+엔지니어"
        "https://search.incruit.com/list/search.asp?col=job&kw=프론트+엔지니어&startno={}"
        
    ],
    "BE": [
        # "https://search.incruit.com/list/search.asp?col=all&src=gsw*www&kw=백엔드+엔지니어"
        "https://search.incruit.com/list/search.asp?col=job&kw=백엔드+엔지니어&startno={}"
    ],
    "DA": [
        # "https://search.incruit.com/list/search.asp?col=all&src=gsw*www&kw=데이터+분석가"
        "https://search.incruit.com/list/search.asp?col=job&kw=데이터+분석가&startno={}"
    ],
    "MLE": [
        # "https://search.incruit.com/list/search.asp?col=all&src=gsw*www&kw=머신러닝+엔지니어"
        "https://search.incruit.com/list/search.asp?col=job&kw=머신러닝+엔지니어&startno={}"
    ]
}

# 데이터를 담을 리스트
links = []  # 크롤링한 모든 링크를 저장
job_for_links = defaultdict(list)  # URL에 여러 직무를 기록하기 위한 구조

# 페이지를 순차적으로 크롤링할 범위 설정
start_page = 0
end_page = 38
page_step = 30  # 페이지네이션의 startno는 30씩 증가

# 오늘 날짜
output_folder = "incruit"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
today = datetime.now().strftime("%Y%m%d")  # 오늘 날짜 (YYYYMMDD)
log_file_name = os.path.join(output_folder, f"{today}.log")

# 어제 날짜로 로그파일 이름 설정
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
yesterday_log_file_name = os.path.join(output_folder, f"{yesterday}.log")

for job_title, url_patterns in job_url_list.items():
    for url_pattern in url_patterns:
        for page in range(start_page, end_page):
            # 페이지네이션을 위한 URL 생성
            url = url_pattern.format(page * page_step)

            try:
                # HTTP 요청 보내기
                response = requests.get(url, timeout=10)  # 10초 제한 설정
                response.raise_for_status()  # HTTP 오류가 있으면 예외 발생
                soup = BeautifulSoup(response.text, 'html.parser')

                # 직무 공고 링크 추출
                job_links_on_page = soup.find_all('a', href=True)

                for link_tag in job_links_on_page:
                    link = link_tag['href']
                    if "jobdb_info" in link:
                        full_link = (
                            "https://www.incruit.com" + link
                            if link.startswith("/")
                            else link
                        )

                        # 모든 링크 추가 (중복 허용)
                        links.append(full_link)

                        # 해당 링크에 직무 추가
                        job_for_links[full_link].append(job_title)

            except requests.exceptions.RequestException as e:
                print(f"Error while fetching {url}: {e}")
                continue



# 어제 로그 파일이 있으면 읽기
previous_urls = {}
if os.path.exists(yesterday_log_file_name):
    with open(yesterday_log_file_name, 'r', encoding='utf-8') as file:
        for line in file.readlines()[1:]:  # 첫 번째 줄은 header
            columns = line.strip().split(',')
            if len(columns) >= 5:
                url = columns[1]
                notice_status = columns[2]
                work_status = columns[3]
                done_time = columns[4]
                job = columns[0]
                previous_urls[url] = {
                    'job': job,
                    'notice_status': notice_status,
                    'work_status': work_status,
                    'done_time': done_time
                }

# 오늘 로그 파일에 기록할 내용 생성
log_data = []

# 오늘 크롤링한 URL과 최근 로그 파일을 비교하여 상태 설정
for url, jobs in job_for_links.items():
    for job in jobs:  # 각 직무마다 따로 기록
        if url in previous_urls:
            notice_status = "exist"
            work_status = previous_urls[url]['work_status']  # 이전 상태 그대로
            done_time = previous_urls[url]['done_time']  # 이전 완료 시간 그대로
        else:
            notice_status = "update"
            work_status = "null"
            done_time = "null"
        log_data.append(f"{job},{url},{notice_status},{work_status},{done_time}")

# 이전 로그 파일에 있지만 오늘 로그 파일에 없는 URL 처리
for url in previous_urls:
    if url not in job_for_links:
        notice_status = "deleted"
        work_status = "done"
        done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 삭제된 시간을 현재 시간으로 설정
        job = previous_urls[url]['job']  # 이전 로그에서 job 값 가져오기
        log_data.append(f"{job},{url},{notice_status},{work_status},{done_time}")

# 로그 파일 저장
with open(log_file_name, 'w', encoding='utf-8') as file:
    # 헤더 작성
    file.write("job,url,notice_status,work_status,done_time\n")
    for line in log_data:
        file.write(line + "\n")
