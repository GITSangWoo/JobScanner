import os
import time
from datetime import datetime
import re
import requests
from uuid import uuid4
import pymysql
import psutil
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from collections import defaultdict
import boto3
import logging
from botocore.exceptions import NoCredentialsError

def kill_existing_chrome():
    """기존 Chrome 프로세스를 강제로 종료합니다."""
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if "chrome" in proc.info["name"].lower():
            proc.kill()

# 로그 디렉토리 설정
log_directory = "/code/crawling/jobkorea"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 로그 파일 경로 설정
log_file_txt = os.path.join(log_directory, "jobkorea_log.txt")

# 로깅 설정
logging.basicConfig(
    filename=log_file_txt,
    level=logging.INFO,
    format="%(message)s"
)

# AWS MySQL 연결 설정
db = pymysql.connect(
    host='t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',  # AWS 퍼블릭 IP
    user='admin',  # MySQL 사용자
    password='dltkddn1',  # MySQL 비밀번호
    database='testdb1',  # 데이터베이스 이름
    port=3306,
    charset='utf8mb4'
)

# 컨테이너 작업 디렉토리 변경
os.chdir("/code/crawling")

# S3 버킷 이름 고정
bucket_name = 't2jt'

# AWS S3 연결 설정
s3_client = boto3.client('s3')

# 커서 생성
cursor = db.cursor()

# 테이블에 데이터 삽입을 위한 SQL 쿼리
insert_query = """
    INSERT INTO combined_table (create_time, update_time, removed_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url, responsibility, qualification, preferential)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

# 작업 상태 기록 함수
def log_status(url, status, task_status):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"{url} - {status} - {task_status} - {time_now}")

# Selenium 웹 드라이버 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
#options.add_argument('--disable-software-rasterizer')  # 소프트웨어 렌더링 비활성화
#options.add_argument("--remote-debugging-port=9222")
#options.add_argument("--window-size=1920x1080")
#options.add_argument("--disable-background-networking")
#options.add_argument("--disable-renderer-backgrounding")
#options.add_argument("--disable-background-timer-throttling")
#options.add_argument("--disable-extensions")
#options.add_argument("--disable-infobars")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# S3에서 파일 읽기 함수
def read_s3_file(bucket_name, file_key):
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = obj['Body'].read().decode('utf-8')
        return set(line.strip() for line in file_content.splitlines())
    except Exception as e:
        print(f"[ERROR] S3 파일 읽기 실패: {file_key}, 에러: {e}")
        return set()

# 가장 최근 날짜 파일 가져오기 (오늘 날짜 제외)
def get_latest_file_exclude_today(bucket_name, prefix, today_date):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' not in response:
        print("S3 버킷에 파일이 존재하지 않습니다.")
        return None
    files = [content['Key'] for content in response['Contents']]
    files = [file for file in files if today_date not in file]
    if not files:
        print("오늘 날짜 파일을 제외한 파일이 없습니다.")
        return None
    files.sort(reverse=True)
    return files[0] if files else None

# 텍스트 및 이미지 디렉토리 생성
text_dir = "jobkorea/jobkorea_txt"
image_dir = "jobkorea/jobkorea_images"
if not os.path.exists(text_dir):
    os.makedirs(text_dir, exist_ok=True)
if not os.path.exists(image_dir):
    os.makedirs(image_dir, exist_ok=True)

processed_count = 0
error_count = 0
error_types = defaultdict(int)
skipped_urls = []

# 변경할 job_title 리스트
job_titles = ["DA", "MLE", "DE", "FE", "BE"]

# 오늘 날짜 계산
today_date = datetime.now().strftime("%Y%m%d")

# 회사 이름을 추출하는 함수
def extract_company(text):
    match = re.search(r"(.*?)(를 소개해요)", text)
    if match:
        return match.group(1).strip()  # "를 소개해요" 앞의 텍스트
    return ""  # "를 소개해요"가 없으면 빈 문자열

def download_image(img_url, image_path):
    try:
        response = requests.get(img_url, stream=True)  # Stream 모드로 다운로드
        if response.status_code == 200:
            content_size = int(response.headers.get('Content-Length', 0))  # 파일 크기 확인
            if content_size < 1024:  # 1KB(1024 bytes) 미만이면 다운로드 중단
                return False
            
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):  # 데이터를 청크 단위로 쓰기
                    file.write(chunk)
            return True
        else:
            return False
    except Exception as e:
        print(f"[ERROR] {img_url}에서 이미지를 다운로드하는 중 오류가 발생했습니다.")
        print(e)
        return False

# S3에 파일 업로드 함수
def upload_to_s3(local_file_path, bucket_name, s3_path):
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_path)
        print(f"[INFO] {local_file_path}를 s3://{bucket_name}에 업로드했습니다.")
        return f"s3://{bucket_name}/{s3_path}"
    except NoCredentialsError:
        print("[ERROR] s3 자격 증명이 없습니다.")
        return None
    except Exception as e:
        print(f"[ERROR] {local_file_path}를 S3로 업로드하는 중 오류가 발생했습니다.")
        return None


processed_urls = set()  # 처리된 URL들을 저장할 집합

# 크롤링 시작 전에 이미 처리된 URL을 읽어옵니다 (예: 데이터베이스나 로그에서).
# 예를 들어, 로그에서 `done` 상태인 URL만 추출하여 `processed_urls`에 추가합니다.
with open(log_file_txt, 'r') as log_file:
    for line in log_file:
        if 'update - done' in line:
            # 로그에서 날짜와 URL 추출
            line_parts = line.split(' ')
            log_date = line_parts[3]  # 날짜는 4번째 항목
            url = line_parts[0]  # URL은 첫 번째 항목
            processed_urls.add(url)

for job_title in job_titles:
    # S3 버킷과 파일 경로 설정
    prefix = f'job/{job_title}/sources/jobkorea/links'
    today_links_file = f"{prefix}/{today_date}.txt"

    # 가장 최근 날짜 파일 가져오기 (오늘 날짜 제외)
    latest_file = get_latest_file_exclude_today(bucket_name, prefix, today_date)

    if not latest_file:
        print(f"{job_title}: 최신 날짜의 파일이 없으므로 오늘 수집된 링크를 모두 크롤링합니다.")
        latest_file = ""
    else:
        latest_date = latest_file.split('/')[-1].split('.')[0]
        latest_links_file = f"{prefix}/{latest_date}.txt"
        print(f"{job_title}: 사용할 파일: {latest_links_file}")

    today_urls = read_s3_file(bucket_name, today_links_file)
    latest_urls = read_s3_file(bucket_name, latest_links_file) if latest_file else set()

    if today_urls:
        if latest_urls:
            new_today_urls = today_urls - latest_urls
            removed_urls = latest_urls - today_urls
            print(f"{job_title}: 새 URL 수: {len(new_today_urls)}, 삭제/마감된 URL 수: {len(removed_urls)}")
        else:
            new_today_urls = today_urls
            removed_urls = set()
            print(f"{job_title}: 새 URL 수: {len(new_today_urls)}, 제거된 URL 수: {len(removed_urls)}")
    else:
        print(f"{job_title}: {today_links_file}을(를) 읽을 수 없습니다.")
        continue

    for url in new_today_urls:
        url = url.strip()
        if not url or url in processed_urls:
            continue

        try:
            driver.get(url)
            time.sleep(17)
            # 페이지가 완전히 로드될 때까지 대기
            #WebDriverWait(driver, 17).until(
            #    lambda driver: driver.execute_script("return document.readyState") == "complete")

            # iframe 전환
            try:
                iframe = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#gib_frame"))
                )
                driver.switch_to.frame(iframe)

                # iframe 내부 텍스트 가져오기
                iframe_body = driver.find_element(By.TAG_NAME, "body")
                iframe_text = iframe_body.text.strip()

                # 이미지 링크를 가져오기 전에 텍스트가 있는지 확인
                img_links = []  # 기본값을 빈 배열로 설정
                if iframe_text == "":  # 텍스트가 없을 경우에만 이미지 링크 추출
                    # iframe 내부 이미지 링크 가져오기 (중복 제거)
                    img_elements = iframe_body.find_elements(By.TAG_NAME, "img")
                    img_links_set = set()  # 중복 제거를 위한 set 사용
                    for img in img_elements:
                        src = img.get_attribute("src")
                        if src:
                            img_links_set.add(src)  # set에 추가
                    img_links = list(img_links_set)  # 중복 제거된 리스트 생성pyt

            except Exception as e:
                # iframe이 없으면 section > article에서 텍스트 추출
                iframe_text = ""
                img_links = []
                content_section = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "section.section-content")))
                article = content_section.find_element(By.CLASS_NAME, "view-content.view-detail")
                iframe_text = article.text.strip()

                # 이미지 링크 추출 (중복 제거)
                img_elements = article.find_elements(By.TAG_NAME, "img")
                img_links_set = set()  # 중복 제거를 위한 set 사용
                for img in img_elements:
                    src = img.get_attribute("src")
                    if src:
                        img_links_set.add(src)  # set에 추가
                img_links = list(img_links_set)  # 중복 제거된 리스트 생성

            # 마감일 정보 수집
            driver.switch_to.default_content()
            deadline = None
            due_type = None
            try:
                date_elements = driver.find_elements(By.CSS_SELECTOR, "dl.date .tahoma")
                if len(date_elements) > 1:  # 시작일과 마감일 둘 다 존재하는 경우
                    deadline_text = date_elements[1].text.strip()  # 두 번째 <span class="tahoma">
                    deadline_match = re.search(r"(\d{4}\.\s*\d{2}\.\s*\d{2})", deadline_text)
                    if deadline_match:
                        deadline = deadline_match.group(1).replace(".", "-").replace(" ", "")  # 2024-12-07 형태로 변환
                        due_type = "날짜"  # 날짜 형식이면 due_type을 "날짜"로 설정

            except Exception as e:
                # deadline이 None일 경우 "상시채용"으로 설정
                print(f"[ERROR] 마감일 정보가 정의되지 않았습니다. {url}")
                error_count += 1
                error_types["<deadline is not defined>"] += 1
                due_type = "상시채용"  # deadline이 없으면 due_type은 "상시채용"으로 설정

            # 회사 이름 및 게시물 제목 수집
            company_name = None
            try:
                summary_section = driver.find_element(By.CLASS_NAME, "secReadSummary")
                company_name = summary_section.find_element(By.CLASS_NAME, "coName").text.strip()
                if not company_name:
                    summary_section = driver.find_element(By.CLASS_NAME, "view-subtitle dev-wrap-subtitle")
            except Exception as e:
                # 회사 이름을 "를 소개해요" 이전 텍스트로 추출
                company_name = extract_company(iframe_text) if company_name == None else company_name

            post_title = None
            try:
                summary_section = driver.find_element(By.CLASS_NAME, "secReadSummary")
                # 기존 제목을 찾고 텍스트를 추출
                post_title = summary_section.find_element(By.CLASS_NAME, "sumTit").text.strip()

                # "닫기" 이후의 텍스트만 추출
                if "닫기" in post_title:
                    post_title = post_title.split("닫기")[1].strip()
            except Exception as e:
                try:
                    # 두 번째 시도: section class="view-title dev-wrap-title"에서 제목 추출
                    title_section = driver.find_element(By.CSS_SELECTOR, "section.view-title.dev-wrap-title")
                    post_title = title_section.text.strip()
                except Exception as e2:
                    print(f"[ERROR] 게시물 제목이 정의되지 않았습니다. {url}")
                    error_count += 1
                    error_types["post_title_not_found"] += 1  # 게시물 제목을 찾을 수 없을 경우 에러 추가
                    post_title = "N/A"  # 게시물 제목을 찾을 수 없으면 'N/A'로 설정

            # 텍스트 파일 및 이미지 URL 업로드
            if iframe_text:  # 텍스트가 비어있지 않으면 텍스트 파일을 생성하고 업로드
                filename = f"{uuid4()}.txt"  # UUID 기반 파일 이름 생성
                file_path = os.path.join(text_dir, filename)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(iframe_text)  # 텍스트 파일 저장

                # S3로 업로드
                s3_text_url = upload_to_s3(file_path, "t2jt", f"job/{job_title}/sources/jobkorea/txt/{filename}")  # 텍스트 파일 업로드
            else:
                s3_text_url = None  # 텍스트가 없으면 s3_text_url은 None으로 설정

            # 이미지 다운로드 및 업로드
            image_urls = []
            for img_url in img_links:
                image_filename = f"{uuid4()}.jpg"  # UUID 기반 이미지 파일 이름 생성
                image_path = os.path.join(image_dir, image_filename)
                if download_image(img_url, image_path):
                    image_url = upload_to_s3(image_path, "t2jt", f"job/{job_title}/sources/jobkorea/images/{image_filename}")
                    if image_url:
                        image_urls.append(image_url)  # 업로드한 이미지 URL을 리스트에 추가


            # DB에 저장할 데이터 준비
            notice_type = None
            if s3_text_url and not image_urls:
                notice_type = "text"
            elif not s3_text_url and image_urls:
                notice_type = "images"
            elif s3_text_url and image_urls:
                notice_type = "both"

            # DB에 저장할 데이터 준비
            data = {
                "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "removed_time": None,
                "site": "jobkorea",
                "job_title": job_title,  # job_title 동적으로 설정
                "due_type": due_type if due_type else "상시채용",
                "due_date": deadline,
                "company": company_name,
                "post_title": post_title,
                "notice_type": notice_type,
                "org_url": url,
                "s3_text_url": s3_text_url,
                "s3_images_url": ", ".join(image_urls) if image_urls else None,
                "responsibility": None,
                "qualification": None,
                "preferential": None
            }

            cursor.execute(insert_query, tuple(data.values()))
            db.commit()

            processed_count += 1
            log_status(url, "update", "done")
        #except Exception as e:
            #skipped_urls.append(url)
            #error_count += 1
            #log_status(url, "update", "failed")
        except Exception as e:
            skipped_urls.append(url)
            error_count += 1
            error_types[str(e)] += 1  # 에러 타입별로 카운트
            log_status(url, "update", f"failed - {e}")  # 에러 메시지 로그 추가
            print(f"[ERROR] 크롤링 실패: {url}, 에러: {e}")

    # removed_time 업데이트
    if removed_urls:
        for removed_url in removed_urls:
            try:
                select_query = "SELECT removed_time FROM combined_table WHERE org_url = %s AND site = 'jobkorea'"
                cursor.execute(select_query, (removed_url,))
                result = cursor.fetchone()
                if result and result[0] is None:
                    update_query = "UPDATE combined_table SET removed_time = %s WHERE org_url = %s AND site = 'jobkorea'"
                    removed_time = datetime.now().strftime("%Y-%m-%d")
                    cursor.execute(update_query, (removed_time, removed_url))
                    db.commit()
            except Exception as e:
                print(f"[ERROR] URL {removed_url} 업데이트 실패: {e}")

# 웹 드라이버 종료
driver.quit()

# MySQL 연결 끊기
db.close()

print(f"[INFO] 처리된 총 개수: {processed_count}")
print(f"[INFO] 오류 개수: {error_count}")
for error_type, count in error_types.items():
    print(f"[INFO] {error_type}: {count}")
