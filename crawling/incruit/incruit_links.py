import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import boto3

# S3 업로드 함수
def upload_to_s3(content, bucket_name, object_name):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Body=content, Bucket=bucket_name, Key=object_name)
        print(f"Uploaded content to S3 bucket {bucket_name} as {object_name}")
        return f"s3://{bucket_name}/{object_name}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

# 검색할 키워드
search_keyword = "데이터 엔지니어"

# 크롤링할 기본 URL
base_url = "https://search.incruit.com/list/search.asp?col=job&kw=%b5%a5%c0%cc%c5%cd+%bf%a3%c1%f6%b4%cf%be%ee&startno={}"

# 데이터를 담을 리스트
links = []

# 페이지를 순차적으로 크롤링할 범위 설정
start_page = 0
end_page = 38
page_step = 30  # 페이지네이션의 startno는 30씩 증가

# 오늘 날짜
output_folder = "links"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
today = datetime.now().strftime("%Y%m%d")  # 오늘 날짜 (YYYYMMDD)
log_file_name = os.path.join(output_folder, f"{today}_incruit.log")

# S3 업로드 경로 설정
bucket_name = "t2jt"
site_name = "incruit"  # 사이트 이름 설정
object_name = f"job/DE/sources/{site_name}/links/{today}.txt"  # S3에서 사용할 객체 이름

# 어제 날짜로 로그파일 이름 설정
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
yesterday_log_file_name = os.path.join(output_folder, f"{yesterday}_incruit.log")


# 페이지 순차적으로 크롤링
for page in range(start_page, end_page):
    startno = page * page_step
    url = base_url.format(startno)
    
    # HTTP 요청 보내기
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 직무 공고 링크 추출 (jobdb_info 클래스에 포함된 a 태그)
    job_links_on_page = soup.find_all('a', href=True)
    
    for link_tag in job_links_on_page:
        link = link_tag['href']
        if "jobdb_info" in link:
            links.append("https://www.incruit.com" + link if link.startswith('/') else link)
    
# 어제 로그 파일이 있으면 읽기
previous_urls = {}
if os.path.exists(yesterday_log_file_name):
    with open(yesterday_log_file_name, 'r', encoding='utf-8') as file:
        for line in file.readlines()[1:]:  # 첫 번째 줄은 header
            columns = line.strip().split(',')
            url = columns[0]
            notice_status = columns[1]
            work_status = columns[2]
            done_time = columns[3]
            previous_urls[url] = {
                'notice_status': notice_status,
                'work_status': work_status,
                'done_time': done_time
            }

# 오늘 로그 파일에 기록할 내용 생성
log_data = []

# 오늘 크롤링한 URL과 어제 로그 파일을 비교하여 상태 설정
for url in links:
    if os.path.exists(yesterday_log_file_name):
        if url in previous_urls:
            # 어제 로그 파일에 URL이 있고, work_status가 "done"이 아니면 그대로 가져옴
            if previous_urls[url]['work_status'] != "done":
                # 작업이 필요하거나 아직 완료되지 않은 경우
                notice_status = previous_urls[url]['notice_status']
                work_status = previous_urls[url]['work_status']
                done_time = previous_urls[url]['done_time']
            else:
                # "done" 상태면 "exist"로 설정하고, done_time을 그대로 사용
                notice_status = "exist"
                work_status = "done"
                done_time = previous_urls[url]['done_time']
        else:
            # 어제 로그 파일에 없으면 상태를 "deleted"로 설정
            notice_status = "deleted"
            work_status = "done"
            done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 삭제된 시간을 현재 시간으로
    else:
        # 어제 로그 파일이 없으면 모든 URL은 "update"로 설정
        notice_status = "update"
        work_status = "null"
        done_time = "null"

    log_data.append(f"{url},{notice_status},{work_status},{done_time}")

# 오늘 로그 파일 생성 (기존 로그 파일 덮어쓰기)
with open(log_file_name, 'w', encoding='utf-8') as file:
    # 헤더 작성
    file.write("url,notice_status,work_status,done_time\n")
    for line in log_data:
        file.write(line + "\n")


