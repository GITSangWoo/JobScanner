import os
import time
import re
import requests
import uuid
import logging
import boto3
import random
import json
import pymysql
import psutil
from uuid import uuid4
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from mysql.connector import pooling
from io import StringIO
from collections import defaultdict
from botocore.exceptions import NoCredentialsError
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import urlparse, parse_qs, parse_qsl, urlencode, urljoin, unquote
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo


def kill_existing_chrome():
    """기존 Chrome 프로세스를 강제로 종료합니다."""
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        if "chrome" in proc.info["name"].lower():
            proc.kill()

# 로그 디렉토리 설정
log_directory = "/code/logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 오늘 날짜로 로그 파일 이름 설정
today = datetime.now().strftime("%Y%m%d")
log_file = os.path.join(log_directory, f"{today}_post.log")

# 로그 설정
logging.basicConfig(
    filename=log_file,  # 로그 파일 경로
    filemode='a',       # 'w'는 매번 덮어씀, 'a'는 이어쓰기
    level=logging.INFO, # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # 로그 메시지 형식
)

# 컨테이너 작업 디렉토리 변경
os.chdir("/code/crawling")

# def jumpit_crawling():
#     try:
#         logging.info("점핏 크롤링 시작")
#         output_folder = f'{os.path.dirname(os.path.abspath(__file__))}/jumpit'
#         if not os.path.exists(output_folder):
#             os.makedirs(output_folder)
#         today = datetime.today().strftime('%Y%m%d')
#         log_file_name = os.path.join(output_folder, f"{today}.log")

#         def save_crawled_content(url, content):
#             file_name = url.split('/')[-1] + ".txt"
#             file_path = os.path.join('textnotice', file_name)
            
#             if not os.path.exists('textnotice'):
#                 os.makedirs('textnotice')
            
#             with open(file_path, 'w', encoding='utf-8') as file:
#                 file.write(content)
#             print(f"Content saved to {file_path}")

#         def insert_into_db(data, connection): 
#             with connection.cursor() as cursor:
#                 sql = """
#                 INSERT INTO combined_table (create_time, update_time, site, job_title, due_type, due_date, company, post_title, org_url, s3_text_url, notice_type)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """
#                 cursor.execute(sql, (
#                     data['create_time'], data['update_time'], data['site'], data['job_title'], data['due_type'], data['due_date'], data['company'],
#                     data['post_title'], data['org_url'], data['s3_text_url'], data['notice_type'],
#                 ))
#                 connection.commit()

#         def update_removed_links_in_db(removed_links, connection):
#             try:
#                 with connection.cursor() as cursor:
#                     for link in removed_links:
#                         sql = """
#                         UPDATE combined_table SET removed_time = %s WHERE org_url = %s AND site = 'jumpit'
#                         """
#                         cursor.execute(sql, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), link))
#                     connection.commit()
#                     print(f"Updated removed links in DB: {len(removed_links)}")
#             except Exception as e:
#                 print(f"Error updating removed links in DB: {e}")

#         def read_links_and_ddays_from_s3(bucket_name, s3_file_key):
#             s3 = boto3.client('s3')
#             try:
#                 response = s3.get_object(Bucket=bucket_name, Key=s3_file_key)
#                 content = response['Body'].read().decode('utf-8')
                
#                 links_with_ddays = {}
#                 for line in content.splitlines():
#                     if ": " in line:
#                         link, d_day = line.strip().split(": ", 1)
#                         link = re.sub(r':\s*\d+$', '', link)
                        
#                         try:
#                             d_day_int = int(d_day)
#                             links_with_ddays[link] = d_day_int
#                         except ValueError:
#                             print(f"Invalid D-day value: {d_day} for URL: {link}")
                
#                 return links_with_ddays
#             except Exception as e:
#                 print(f"Error reading file from S3: {e}")
#                 return {}

#         def upload_to_s3(file_path, bucket_name, object_name):
#             s3 = boto3.client('s3')
#             try:
#                 s3.upload_file(file_path, bucket_name, object_name)
#                 print(f"Uploaded {file_path} to S3 bucket {bucket_name} as {object_name}")
#                 return f"s3://{bucket_name}/{object_name}"
#             except Exception as e:
#                 print(f"Error uploading file to S3: {e}")
#                 return None

#         def extract_site_name(url):
#             parsed_url = urlparse(url)
#             domain = parsed_url.hostname
#             return domain.split('.')[0] if domain else None

#         def ensure_directories():
#             os.makedirs("links", exist_ok=True)

#         def calculate_deadline_from_dday(d_day):
#             today = datetime.now().date()
#             deadline = today + timedelta(days=d_day)
#             return deadline

#         def update_log_file(url, crawl_time):
#             with open(log_file_name, 'r', encoding='utf-8') as file:
#                 lines = file.readlines()

#             updated_lines = []
            
#             for line in lines:
#                 columns = line.strip().split(',')
#                 if columns[0] == url:
#                     columns[2] = "done"
#                     columns[3] = crawl_time
#                     updated_line = ','.join(columns)
#                     updated_lines.append(updated_line + '\n')
#                 else:
#                     updated_lines.append(line)
            
#             with open(log_file_name, 'w', encoding='utf-8') as file:
#                 file.writelines(updated_lines)

#         ensure_directories()

#         bucket_name = 't2jt'
#         today_file_key = f"job/DE/sources/jumpit/links/{today}.txt"

#         # links_with_ddays = read_links_and_ddays_from_s3(bucket_name, today_file_key)

#         # urls_to_crawl = list(links_with_ddays.keys())

#         connection = pymysql.connect(
#             host='t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',
#             user='admin',
#             password='dltkddn1',
#             database='testdb1',
#             port=3306
#         )

#         options = Options()
#         options.add_argument("--headless")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-gpu")
#         options.add_argument('--disable-software-rasterizer')  # 소프트웨어 렌더링 비활성화
#         options.add_argument("--remote-debugging-port=9222")
#         options.add_argument("--window-size=1920x1080")
#         options.add_argument("--disable-background-networking")
#         options.add_argument("--disable-renderer-backgrounding")
#         options.add_argument("--disable-background-timer-throttling")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--disable-infobars")
        
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#         with open(log_file_name, 'r', encoding='utf-8') as file:
#             lines = file.readlines()

#             removed_links = []

#             for line in lines[1:]:
#                 columns = line.strip().split(',')
#                 url = columns[0]
#                 notice_status = columns[1]
#                 work_status = columns[2]
#                 done_time = columns[3]
#                 d_day = columns[4]  # D-day 값을 가져옴
                
#                 logging.info(f"처리할 URL: {url}, 상태: {notice_status}, 작업 상태: {work_status}")

#                 # D-day 값이 숫자인 경우 deadline 계산
#                 try:
#                     d_day_int = int(d_day)
#                     deadline = calculate_deadline_from_dday(d_day_int)
#                 except ValueError:
#                     deadline = None  # D-day 값이 유효하지 않으면 deadline은 None
                
#                 if notice_status == "deleted":
#                     removed_links.append(url)
#                 elif notice_status == "update" and work_status == "null":
#                     print(f"Starting crawl for {url}")
#                     crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#                     # Open the URL and perform web scraping directly
#                     try:
#                         try:
#                             driver.get(url)
#                             time.sleep(3)  # Wait for the page to load
#                             logging.info(f"URL 로드 성공: {url}")
#                         except Exception as e:
#                             logging.error(f"URL 로드 실패: {url}, 에러: {e}")

#                         # Extract job content
#                         job_content_text = None
#                         try:
#                             job_content_section = WebDriverWait(driver, 30).until(
#                                 EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-10492dab-3.hiVlDL"))  # Adjust this selector to match the correct element
#                             )
#                             job_content_text = job_content_section.text
#                             logging.info(f"콘텐츠 추출 성공: {url}")
#                         except Exception as e:
#                             logging.error(f"콘텐츠 추출 실패: {url}, 에러: {e}")
#                             continue  # 다음 URL로 넘어감
                        
#                         # If content is found, save to file and upload to S3
#                         if job_content_text:
#                             try:
#                                 text_path = os.path.join("texts", f"{uuid.uuid4()}.txt")
#                                 with open(text_path, "w", encoding="utf-8") as f:
#                                     f.write(job_content_text)
#                                 s3_text_url = upload_to_s3(text_path, bucket_name, f"job/DE/sources/{extract_site_name(url)}/txt/{uuid.uuid4()}.txt")
#                                 logging.info(f"콘텐츠 저장 및 S3 업로드 성공: {s3_text_url}")
#                             except Exception as e:
#                                 logging.error(f"콘텐츠 저장/업로드 실패: {url}, 에러: {e}")
#                                 continue
                        
#                         # Extract additional info (like company name, post title)
#                         company_name = None
#                         post_title = None
#                         try:
#                             company_link = WebDriverWait(driver, 10).until(
#                                 EC.presence_of_element_located((By.CSS_SELECTOR, "a.name"))
#                             )
#                             company_name = parse_qs(urlparse(company_link.get_attribute("href")).query).get("company_nm", [None])[0]

#                             post_title_element = WebDriverWait(driver, 10).until(
#                                 EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
#                             )
#                             post_title = post_title_element.text
#                         except Exception:
#                             pass

#                         # Determine due type
#                         due_type = '상시채용' if not deadline else '날짜'
#                         due_date = deadline if deadline else None

#                         # Prepare data for DB insertion
#                         data = {
#                             'site': extract_site_name(url),
#                             'job_title': '데이터 엔지니어',
#                             'due_type': due_type,
#                             'due_date': due_date,
#                             'company': company_name,
#                             'notice_type': 'text',
#                             'post_title': post_title,
#                             'org_url': url,
#                             's3_text_url': s3_text_url,
#                             's3_image_url': None,
#                             'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                             'update_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                         }

#                         try:
#                             insert_into_db(data, connection)  # Insert the data into the DB
#                             logging.info(f"DB 삽입 성공: {url}")
#                         except Exception as e:
#                             logging.error(f"DB 삽입 실패: {url}, 에러: {e}")
#                             continue
#                         try:
#                             update_log_file(url, crawl_time)  # Update log file
#                             logging.info(f"로그 파일 업데이트 성공: {url}")
#                         except Exception as e:
#                             logging.error(f"로그 파일 업데이트 실패: {url}, 에러: {e}")
#                             continue

#                     except Exception as e:
#                         logging.error(f"URL 처리 실패: {url}, 에러: {e}")

#             if removed_links:
#                 update_removed_links_in_db(removed_links, connection)  # Update removed links in DB

#         driver.quit()
#         connection.close()

#         logging.info("점핏 크롤링 완료")
#     except Exception as e:
#         logging.error(f"점핏 크롤링 중 오류 발생: {e}")


def wanted_crawling():
    try:
        logging.info("원티드 크롤링 시작")
        # AWS S3 클라이언트 설정
        s3_client = boto3.client('s3')

        # MySQL 연결 설정
        connection = pymysql.connect(
            host='t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',
            user='admin',
            password='dltkddn1',
            database='testdb1',
            port=3306
        )
        cursor = connection.cursor()

        # S3 버킷과 폴더 경로 설정
        s3_bucket_name = 't2jt'

        # 셀레니움 웹 드라이버 설정
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

        # 오늘 날짜로 로그파일 이름 설정
        today = datetime.today().strftime('%Y%m%d')
        log_file_name = f"{os.path.dirname(os.path.abspath(__file__))}/wanted/{today}.log"
        error_log_file_name = f"{os.path.dirname(os.path.abspath(__file__))}/wanted/{today}_error.log"  # 에러 로그 파일

        # 크롤링한 콘텐츠를 로컬에 저장하고, S3에 업로드 후 URL 반환
        def save_crawled_content(url, content, job_title, max_retries=3):
            attempt = 0
            while attempt < max_retries:
                try:
                    file_name = f"{uuid.uuid4()}.txt"  # UUID로 파일 이름 생성
                    # 동적으로 경로 설정 (job_title을 포함하여 경로 생성)
                    s3_folder_path_dynamic = f"job/{job_title}/sources/wanted/txt/"
                    
                    # S3에 파일 업로드
                    s3_file_path = os.path.join(s3_folder_path_dynamic, file_name)
                    s3_client.put_object(
                        Bucket=s3_bucket_name,
                        Key=s3_file_path,  # 동적으로 생성된 경로로 파일 업로드
                        Body=content,
                        ContentType='text/plain'
                    )
                    s3_url = f"s3://{s3_bucket_name}/{s3_file_path}"
                    print(f"Content uploaded to S3 at {s3_url}")
                    return s3_url  # S3 URL 반환
                except Exception as e:
                    attempt += 1
                    print(f"Attempt {attempt} failed for {url} during S3 upload: {e}")
                    if attempt < max_retries:
                        print("Retrying...")
                        time.sleep(2)  # 2초 대기 후 재시도
                    else:
                        print(f"All {max_retries} attempts failed for {url}. Giving up.")
                        
                        # S3 업로드 오류를 에러 로그 파일에 기록
                        error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        with open(error_log_file_name, 'a', encoding='utf-8') as error_log:
                            error_log.write(f"{error_time}, {url}, S3 upload error: {str(e)}\n")
                        
                        return None

        # 페이지 크롤링 함수
        def crawl_url(url, job_title, max_retries=3):
            attempt = 0
            while attempt < max_retries:
                try:
                    driver.get(url)
                    time.sleep(3)  # 페이지 로딩 대기
                    
                    # "상세 정보 더 보기" 버튼을 기다리고 클릭
                    more_button = WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '상세 정보 더 보기')]"))
                    )

                    # 버튼이 화면에 보이지 않으면 스크롤하여 화면에 표시
                    driver.execute_script("arguments[0].scrollIntoView(true);", more_button)
                    time.sleep(1)  # 스크롤 후 잠시 대기

                    # 버튼 클릭 시도
                    driver.execute_script("arguments[0].click();", more_button)

                    # 클릭 후 로딩된 콘텐츠 가져오기
                    job_content_section = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "section.JobContent_JobContent__qan7s"))
                    )

                    # 섹션 내의 텍스트 내용 가져오기
                    job_content_text = job_content_section.text

                    # 회사 이름, 공고 제목, 마감일 추출
                    company_name = driver.find_element(By.CSS_SELECTOR, "a.JobHeader_JobHeader__Tools__Company__Link__zAvYv").get_attribute("data-company-name")
                    post_title = driver.find_element(By.CSS_SELECTOR, "h1.JobHeader_JobHeader__PositionName__kfauc").text
                    deadline = driver.find_element(By.CSS_SELECTOR, "span.wds-lgio6k").text.strip() if driver.find_elements(By.CSS_SELECTOR, "span.wds-lgio6k") else "Unknown Deadline"
                    
                    # 마감일 처리
                    if re.match(r"\d{4}\.\d{2}\.\d{2}", deadline):  # 날짜 형식 (2024.12.02) 확인
                        due_type = "날짜"
                        due_date = datetime.strptime(deadline, "%Y.%m.%d").date()  # 날짜 형식 변환
                    else:
                        due_type = deadline
                        due_date = None
                    
                    # S3에 텍스트 내용 저장 후 URL 반환
                    s3_text_url = save_crawled_content(url, job_content_text, job_title)
                    
                    if not s3_text_url:
                        # S3 업로드 실패 시 에러 처리
                        update_log_file(url, "Error", status="error")
                        return "Error during crawling."
                    
                    # 데이터베이스에 메타 데이터 삽입
                    create_time = update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    job_data = {
                        'create_time': create_time,
                        'update_time': update_time,
                        'removed_time': None,
                        'site': 'wanted',
                        'job_title': job_title,  # 동적으로 받아온 job_title 사용
                        'due_type': due_type,
                        'due_date': due_date,
                        'company': company_name,
                        'post_title': post_title,
                        'notice_type': 'text',
                        'org_url': url,
                        's3_text_url': s3_text_url,
                        's3_images_url': None,
                        'responsibility': None,
                        'qualification': None,
                        'preferential': None
                    }
                    insert_query = """
                    INSERT INTO combined_table (create_time, update_time, removed_time, site, job_title, due_type, due_date, company, 
                                        post_title, notice_type, org_url, s3_text_url, s3_images_url, responsibility, qualification, preferential)
                    VALUES (%(create_time)s, %(update_time)s, %(removed_time)s, %(site)s, %(job_title)s, %(due_type)s, %(due_date)s, %(company)s, 
                            %(post_title)s, %(notice_type)s, %(org_url)s, %(s3_text_url)s, %(s3_images_url)s, %(responsibility)s, %(qualification)s, %(preferential)s)
                    """
                    cursor.execute(insert_query, job_data)
                    connection.commit()

                    # 크롤링 성공 시 log 파일 업데이트
                    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_log_file(url, crawl_time, status="done")
                    
                    return job_content_text
                except Exception as e:
                    attempt += 1
                    print(f"Attempt {attempt} failed for {url}: {e}")
                    if attempt < max_retries:
                        print("Retrying...")
                        time.sleep(2)  # 2초 대기 후 재시도
                    else:
                        print(f"All {max_retries} attempts failed for {url}. Giving up.")
                        
                        # 에러 로그 파일에 기록
                        error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        with open(error_log_file_name, 'a', encoding='utf-8') as error_log:
                            error_log.write(f"{error_time}, {url}, {str(e)}\n")
                        
                        # 에러 발생 시 log 파일에서 work_status를 'error'로 변경하고 done_time 업데이트
                        update_log_file(url, error_time, status="error")
                        return "Error during crawling."

        # 로그 파일을 읽고 해당 URL의 작업 상태 업데이트
        def update_log_file(url, done_time, status="done"):
            try:
                with open(log_file_name, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                updated_lines = []
                for line in lines:
                    columns = line.strip().split(',')
                    if columns[1] == url:  # job_title을 사용하여 매칭
                        job_title = columns[0]  # job_title을 첫 번째 열에서 가져옵니다.
                        columns[3] = status  # 상태를 'done' 또는 'error'로 변경
                        columns[4] = done_time  # done_time을 업데이트
                        updated_line = ','.join(columns) + '\n'
                        updated_lines.append(updated_line)
                    else:
                        updated_lines.append(line)

                # 변경된 내용을 파일에 다시 작성
                with open(log_file_name, 'w', encoding='utf-8') as file:
                    file.writelines(updated_lines)

                print(f"Log file updated for URL {url}")
            except Exception as e:
                print(f"Error updating log file for URL {url}: {e}")

        # 로그에 따라 'deleted', 'update', 'exist' 상태인 URL만 크롤링

        def main():
            with open(log_file_name, 'r', encoding='utf-8') as file:
                lines = file.readlines()

            for line in lines[1:]:  # 첫 번째 줄은 헤더이므로 생략
                columns = line.strip().split(',')
                url = columns[1]
                notice_status = columns[2]
                work_status = columns[3]
                done_time = columns[4] if len(columns) > 4 else None  # done_time이 존재할 때만 처리
                job_title = columns[0]  # 첫 번째 열에서 job_title을 가져옵니다.

                # 'deleted' 상태일 경우 처리 (크롤링은 하지 않음)
                if notice_status == "deleted":
                    print(f"URL {url} is deleted. Checking if it exists in the database.")
                    cursor.execute("SELECT removed_time FROM combined_table WHERE org_url = %s", (url,))
                    result = cursor.fetchone()

                    if result:
                        removed_time = done_time  # 로그에서 가져온 done_time 값을 removed_time으로 사용
                        print(f"URL {url} exists in DB. Updating removed_time to: {removed_time}")
                        # 데이터베이스에서 removed_time을 done_time으로 업데이트
                        update_time_query = """
                        UPDATE combined_table
                        SET removed_time = %s
                        WHERE org_url = %s AND site = 'wanted'
                        """
                        cursor.execute(update_time_query, (removed_time, url))
                        connection.commit()
                        print(f"Removed time for {url} updated successfully.")
                    else:
                        print(f"URL {url} not found in the database.")
                    continue  # 'deleted' 상태인 경우 크롤링을 건너뛰고, 제거만 처리

                # 'update' 또는 'exist' 상태이면서 'work_status'가 'null' 또는 'error'인 URL만 크롤링
                if notice_status in ['update', 'exist'] and (work_status == 'null' or work_status == 'error'):
                    print(f"Crawling URL: {url}")
                    crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # 크롤링 함수 실행
                    crawl_result = crawl_url(url, job_title)  # 크롤링 함수 실행

                    # 크롤링이 성공적으로 완료되면 로그 파일에서 work_status를 done으로 업데이트
                    if crawl_result != "Error during crawling.":
                        update_log_file(url, crawl_time)

            # 브라우저 종료
            driver.quit()

            logging.info("원티드 크롤링 완료")
    except Exception as e:
        logging.error(f"원티드 크롤링 중 오류 발생: {e}")


# def incruit_crawling():
#     try:
#         logging.info("인크루트 크롤링 시작")
#         # MySQL 연결 풀 설정
#         db_config = {
#             'user': 'admin',
#             'password': 'dltkddn1',
#             'host': 't2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',
#             'database': 'testdb1',
#             'port': 3306
#         }

#         connection_pool = pooling.MySQLConnectionPool(pool_name="testdb1_pool", pool_size=5, **db_config)

#         def insert_into_db(data):
#             try:
#                 connection = connection_pool.get_connection()
#                 cursor = connection.cursor()

#                 sql = """
#                 INSERT INTO combined_table (create_time, update_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url) 
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                 """
#                 values = (
#                     data['create_time'], data['update_time'], data['site'], data['job_title'], data['due_type'], data['due_date'], data['company'],
#                     data['post_title'], data['notice_type'], data['org_url'], data['s3_text_url'], data['s3_image_url'],  
#                 )
#                 cursor.execute(sql, values)
#                 connection.commit()
#                 print(f"Data inserted into DB: {data['post_title']}")

#             except Exception as e:
#                 print(f"Error inserting data into DB: {e}")
#             finally:
#                 if 'cursor' in locals():
#                     cursor.close()
#                 if 'connection' in locals():
#                     connection.close()

#         def update_removed_links_in_db(removed_links):
#             try:
#                 connection = connection_pool.get_connection()
#                 cursor = connection.cursor()

#                 for link in removed_links:
#                     sql = """UPDATE combined_table SET removed_time = %s WHERE org_url = %s AND site = 'incruit'"""
#                     cursor.execute(sql, (datetime.now(), link))

#                 connection.commit()
#                 print(f"Updated removed links in DB: {len(removed_links)}")

#             except Exception as e:
#                 print(f"Error updating removed links in DB: {e}")
#             finally:
#                 if 'cursor' in locals():
#                     cursor.close()
#                 if 'connection' in locals():
#                     connection.close()

#         def upload_to_s3(content, bucket_name, object_name):
#             try:
#                 s3 = boto3.client('s3')
                
#                 # 만약 content가 문자열이면, 이를 바이트로 인코딩
#                 if isinstance(content, str):
#                     content = content.encode('utf-8')
                
#                 # S3에 업로드
#                 s3.put_object(Bucket=bucket_name, Key=object_name, Body=content)
#                 print(f"Uploaded to S3 as {object_name}")
#                 return f"s3://{bucket_name}/{object_name}"
#             except Exception as e:
#                 print(f"Error uploading to S3: {e}")
#                 return None

#         def download_from_s3_direct(s3_uri):
#             try:
#                 s3_uri_parts = s3_uri.replace("s3://", "").split("/", 1)
#                 bucket_name = s3_uri_parts[0]
#                 object_name = s3_uri_parts[1]

#                 s3_client = boto3.client('s3')
#                 obj = s3_client.get_object(Bucket=bucket_name, Key=object_name)
#                 file_content = obj['Body'].read().decode('utf-8')

#                 print(f"Successfully read from S3: {s3_uri}")
#                 return file_content
#             except Exception as e:
#                 print(f"Error reading from S3: {e}")
#                 return None

#         def process_images(image_urls, job_id, img_folder, bucket_name, s3_folder):
#             s3_image_urls = []
#             for i, img_url in enumerate(image_urls):
#                 try:
#                     img_filename = f"{job_id}_image_{i + 1}.jpg"
#                     # 이미지를 로컬에 저장하지 않고 직접 메모리로 처리
#                     img_url_data = requests.get(img_url).content
#                     s3_image_url = upload_to_s3(img_url_data, bucket_name, f"{s3_folder}/{img_filename}")
#                     if s3_image_url:
#                         s3_image_urls.append(s3_image_url)
#                 except Exception as e:
#                     print(f"Error processing image {img_url}: {e}")
#             return s3_image_urls

#         def convert_to_mysql_date(due_date):
#             match = re.match(r'(\d{4})\.(\d{2})\.(\d{2})', due_date)
#             return f"{match.group(1)}-{match.group(2)}-{match.group(3)}" if match else None

#         # 크롤링 타임아웃을 위한 기본 설정
#         CRAWL_TIMEOUT = 30  # 30초로 설정

#         # Chrome 설정
#         options = Options()
#         options.add_argument("--headless")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-gpu")
#         options.add_argument('--disable-software-rasterizer')  # 소프트웨어 렌더링 비활성화
#         options.add_argument("--remote-debugging-port=9222")
#         options.add_argument("--window-size=1920x1080")
#         options.add_argument("--disable-background-networking")
#         options.add_argument("--disable-renderer-backgrounding")
#         options.add_argument("--disable-background-timer-throttling")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--disable-infobars")
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#         # 오늘 날짜로 로그파일 이름 설정
#         output_folder = f'{os.path.dirname(os.path.abspath(__file__))}/incruit'
#         today = datetime.today().strftime('%Y%m%d')
#         log_file_name = os.path.join(output_folder, f"{today}.log")  # 로컬 파일 사용

#         # DB 연결을 크롤링 시작 전에 한 번만 열고, 크롤링이 다 끝난 후 connection.close() 호출
#         connection = connection_pool.get_connection()

#         # 기존 로그 파일을 읽고, "update" 상태인 URL들만 크롤링
#         def update_log_file(url, crawl_time):
#             # 로그 파일을 읽고, 해당 URL의 상태 업데이트
#             with open(log_file_name, 'r', encoding='utf-8') as file:
#                 lines = file.readlines()

#             # 새로운 데이터를 담을 리스트
#             updated_lines = []
            
#             for line in lines:
#                 columns = line.strip().split(',')
#                 if columns[0] == url:
#                     # URL이 일치하면 work_status를 "done"으로 업데이트하고, done_time 추가
#                     columns[2] = "done"
#                     columns[3] = crawl_time
#                     updated_line = ','.join(columns)
#                     updated_lines.append(updated_line + '\n')
#                 else:
#                     # 일치하지 않으면 기존 라인을 그대로 추가
#                     updated_lines.append(line)
            
#             # 로그 파일을 덮어쓰기 (한 줄씩 업데이트)
#             with open(log_file_name, 'w', encoding='utf-8') as file:
#                 file.writelines(updated_lines)

#         # 기존 로그 파일을 읽기
#         with open(log_file_name, 'r', encoding='utf-8') as file:
#             lines = file.readlines()

#             # 'update' 상태인 URL들을 크롤링 대상 리스트에 추가
#             removed_links = []

#             for line in lines[1:]:
#                 columns = line.strip().split(',')
#                 url = columns[0]
#                 notice_status = columns[1]
#                 work_status = columns[2]
#                 done_time = columns[3]
                
#                 if notice_status == "update" and work_status == "null":
#                     print(f"Starting crawl for {url}")
#                     # 크롤링 작업 수행
#                     crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#                     try:
#                         # 각 링크에 대해 로딩 타임아웃 설정
#                         driver.get(url)
#                         driver.set_page_load_timeout(CRAWL_TIMEOUT)  # 페이지 로딩 타임아웃을 설정합니다.
#                         time.sleep(3)

#                         company = WebDriverWait(driver, 10).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, ".job_info_detail .top-cnt a"))
#                         ).text.strip()
#                         post_title = WebDriverWait(driver, 10).until(
#                             EC.presence_of_element_located((By.CSS_SELECTOR, ".job_info_detail .top-cnt h1"))
#                         ).text.strip()

#                         # 마감 날짜 추출
#                         due_type, due_date_mysql = "NULL", None
#                         try:
#                             reception_section = WebDriverWait(driver, 10).until(
#                                 EC.presence_of_element_located((By.CSS_SELECTOR, ".reception"))
#                             )
#                             deadline_elements = reception_section.find_elements(By.CSS_SELECTOR, ".intxt.end .day em")
#                             if deadline_elements:
#                                 due_type = "날짜"
#                                 due_date_mysql = convert_to_mysql_date(deadline_elements[0].text.strip())
#                             else:
#                                 status_elements = reception_section.find_elements(By.CSS_SELECTOR, ".d_day.pts")
#                                 due_type = status_elements[0].text.strip() if status_elements else "NULL"
#                         except Exception as e:
#                             print(f"Error extracting deadline: {e}")

#                         iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ifrmJobCont")))
#                         driver.switch_to.frame(iframe)
#                         content_job_section = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "content_job")))

#                         text_content = content_job_section.text.strip()
#                         image_urls = [img.get_attribute("src") for img in content_job_section.find_elements(By.TAG_NAME, "img")]
#                         driver.switch_to.default_content()

#                         job_id = str(uuid.uuid4())
#                         text_filename = f"{job_id}.txt"
#                         s3_text_url = upload_to_s3(text_content, "t2jt", f"job/DE/sources/incruit/txt/{job_id}.txt")

#                         s3_image_urls = process_images(image_urls, job_id, "./images", "t2jt", "job/DE/sources/incruit/images")

#                         notice_type = "both" if s3_text_url and s3_image_urls else "text" if s3_text_url else "images" if s3_image_urls else "NULL"

#                         insert_into_db({
#                             "site": "incruit",
#                             "job_title": "데이터 엔지니어",
#                             "due_type": due_type,
#                             "due_date": due_date_mysql,
#                             "company": company,
#                             "post_title": post_title,
#                             "notice_type": notice_type,
#                             "org_url": url,
#                             "s3_text_url": s3_text_url,
#                             "s3_image_url": ";".join(s3_image_urls),
#                             "create_time": datetime.now(),
#                             "update_time": datetime.now(),
#                         })

#                         # 작업 완료 후 로그 파일 업데이트
#                         update_log_file(url, crawl_time)

#                     except Exception as e:
#                         print(f"Error processing {url}: {e}")

#                 elif notice_status == "deleted":
#                     removed_links.append(url)

#             if removed_links:
#                 update_removed_links_in_db(removed_links)

#         # 크롤링 완료 후 DB 연결 종료
#         connection.close()

#         driver.quit()

#         logging.info("인크루트 크롤링 완료")
#     except Exception as e:
#         logging.error(f"인크루트 크롤링 중 오류 발생: {e}")


# def rocketpunch_crawling():
#     try:
#         logging.info("로켓펀치 크롤링 시작")
#         kst = ZoneInfo("Asia/Seoul")

#         # AWS S3 클라이언트 설정
#         s3 = boto3.client('s3')

#         # 변수 설정 : 링크 저장을 위한 S3
#         BUCKET_NAME = 't2jt'
#         S3_LINK_PATH = 'job/{abb}/airflow_test/rocketpunch/links/'
#         S3_TEXT_PATH = 'job/{abb}/airflow_test/rocketpunch/txt/'
#         S3_IMAGE_PATH = 'job/{abb}/airflow_test/rocketpunch/images/'  

#         # MySQL 연결 설정
#         connection = pymysql.connect(
#             host='t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',
#             user='admin',
#             password='dltkddn1',
#             database='testdb1',
#             port=3306
#         )
        
#         cursor = connection.cursor()

#         # 변수 설정 : 검색 키워드
#         job_titles = {
#             "DE":"데이터 엔지니어", 
#             "DA":"데이터 분석가", 
#             "FE":"프론트엔드 엔지니어", 
#             "BE":"백엔드 엔지니어", 
#             "MLE":"머신러닝 엔지니어"
#         }

#         # User-Agent 문자열
#         user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"

#         chrome_options = Options()
#         chrome_options.add_argument(f"user-agent={user_agent}")
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument('--disable-software-rasterizer')  # 소프트웨어 렌더링 비활성화
#         chrome_options.add_argument("--remote-debugging-port=9222")
#         chrome_options.add_argument("--window-size=1920x1080")
#         chrome_options.add_argument("--disable-background-networking")
#         chrome_options.add_argument("--disable-renderer-backgrounding")
#         chrome_options.add_argument("--disable-background-timer-throttling")
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-infobars")

#         # Selenium 웹 드라이버 설정
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

#         # 페이지 크롤링 함수
#         def get_job_posts(link, job_title, s3_text_path, s3_image_path):
#             try:
#                 # 링크에서 텍스트 크롤링
#                 print(f"해당 링크: {link}에서 채용공고 상세 크롤링 진행중")
#                 driver.get(link)
#                 time.sleep(random.uniform(1, 2))  # 페이지 로딩 1 ~ 2초 대기

#                 # 스크롤 내려서 로그인 팝업 뜨도록 설정
#                 previous_height = driver.execute_script("return document.body.scrollHeight")
#                 while True:
#                     # 스크롤을 일정 간격으로 내리기
#                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                     # 새로운 페이지 높이를 가져오기
#                     new_height = driver.execute_script("return document.body.scrollHeight")
#                     # 이전 높이와 새 높이가 같으면 더 이상 스크롤할 필요가 없으므로 종료
#                     if new_height == previous_height:
#                         break
#                     previous_height = new_height  # 이전 높이 업데이트

#                 # 로그인 팝업창 닫기 버튼 클릭
#                 try:
#                     close_popup_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.XPATH, '/html/body/div[13]/div/i'))
#                     )
#                     close_popup_button.click()
#                     #print("팝업창 닫기 버튼 클릭 성공")
#                 except Exception as e:
#                     print("팝업창이 없거나 닫기 버튼을 찾을 수 없습니다.")


#                 ## 더보기 버튼 1
#                 try:
#                     more_button = WebDriverWait(driver, 5).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(3) > div > a'))
#                     )
#                     actions = ActionChains(driver)
#                     actions.move_to_element(more_button).click().perform()
#                     #print("첫번째 더보기를 감지하고 눌렀습니다")
#                 except Exception as e:
#                     pass

#                 ## 더보기 버튼 2
#                 try:
#                     more_button2 = WebDriverWait(driver, 5).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(7) > div.content.break > a'))
#                     )
#                     actions2 = ActionChains(driver)
#                     actions2.move_to_element(more_button2).click().perform()
#                     #print("두번째 더보기를 감지하고 눌렀습니다")
#                 except Exception as e:
#                     pass

#                 ## 더보기 버튼 2.5
#                 try:
#                     more_button3 = WebDriverWait(driver, 5).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(7) > div > a'))
#                     )
#                     actions3 = ActionChains(driver)
#                     actions3.move_to_element(more_button3).click().perform()
#                     #print("세번째 더보기를 감지하고 눌렀습니다")
#                 except Exception as e:
#                     pass

#                 # due_type, due_date 크롤링에서 긁어오기
#                 try:
#                     deadline_element = WebDriverWait(driver, 10).until(   
#                         EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > div.four.wide.job-infoset.column > div.ui.celled.grid > div:nth-child(3) > div > div:nth-child(6) > div.content'))
#                     )
#                     deadline = deadline_element.text
#                     if re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
#                         due_type = "날짜"
#                         due_date = datetime.strptime(deadline, "%Y-%m-%d").strftime("%Y-%m-%d")
#                     else:
#                         # due_type = deadline
#                         due_type = deadline[:20] if len(deadline.encode('utf-8')) <= 20 else deadline.encode('utf-8')[:20].decode('utf-8', 'ignore')
#                         due_date = None
#                 except Exception as e:
#                     print("마감 기한을 찾을 수 없습니다. 해당 요소가 로드되지 않았습니다:", e)
#                     due_type = "unknown"
#                     due_date = None
                
#                 # 회사 이름 요소 감지
#                 try:
#                     company_element = WebDriverWait(driver, 10).until(
#                         EC.presence_of_element_located((By.CLASS_NAME, 'nowrap.company-name'))
#                     )
#                     company_name = company_element.text
#                 except Exception as e:
#                     company_name = "unknown"
#                     print("회사 이름을 찾을 수 없습니다:", e)
                
#                 # 공고 제목 요소 감지
#                 try:
#                     post_title_element = WebDriverWait(driver, 10).until(
#                         EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > div.four.wide.job-infoset.column > div.ui.celled.grid > div:nth-child(3) > h2'))
#                     )
#                     post_title = post_title_element.text
#                 except Exception as e:
#                     post_title = "unknown"
#                     print("공고 제목을 찾을 수 없습니다:", e)

#                 # 여기서 부터 공고에서 텍스트, 이미지 감지 > 텍스트와 이미지 s3에 저장후 url 반환
#                 div_selectors = [
#                     '#wrap > div.eight.wide.job-content.column > section:nth-child(3)',   # 주요업무
#                     '#wrap > div.eight.wide.job-content.column > section:nth-child(5)',   # 업무기술/활동분야
#                     '#wrap > div.eight.wide.job-content.column > section:nth-child(7)',   # 채용상세
#                     '#wrap > div.eight.wide.job-content.column > section:nth-child(11)'   # 산업분야
#                 ]  
#                 # process_content에서 notice_type, text, image 탐지하고 text, image는 바로 s3에 저장
#                 # 그리고 저장된 각각의 s3의 주소를 반환
#                 notice_type, image_paths, text_path = process_contents(div_selectors, s3_text_path, s3_image_path)
#                 s3_images_url = ",".join(image_paths) if image_paths else None

#                 create_time = update_time = datetime.now(tz=kst).strftime("%Y-%m-%d %H:%M:%S") 
#                 job_post = {
#                     'create_time': create_time,
#                     'update_time': update_time,
#                     'removed_time': None,
#                     'site': 'rocketpunch',
#                     'job_title': job_title,  # 동적으로 받아온 job_title 사용
#                     'due_type': due_type,
#                     'due_date': due_date,
#                     'company': company_name,
#                     'post_title': post_title,
#                     'notice_type': notice_type,
#                     'org_url': link,
#                     's3_text_url': text_path,
#                     's3_images_url': s3_images_url,
#                     'responsibility': None,
#                     'qualification': None,
#                     'preferential': None
#                 }
                
#                 query = """
#                 INSERT INTO combined_table (create_time, update_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url)
#                 VALUES (%(create_time)s, %(update_time)s, %(site)s, %(job_title)s, %(due_type)s, %(due_date)s, %(company)s, 
#                         %(post_title)s, %(notice_type)s, %(org_url)s, %(s3_text_url)s, %(s3_images_url)s);
#                 """
#                 cursor.execute(query, job_post)
#                 connection.commit()

#             except Exception as e:
#                 print(f"❌ 데이터 삽입 실패 (job_post: {job_post.get('org_url')}): {str(e)}")
#             finally:
#                 driver.quit()
            
#         # 이 안에서 S3 method import 피일보내고 url 반환 / db method 메타데이터 보내고 url도 입력
#         # for loop 마다 db로 보내면 중간
#         def process_contents(div_selectors, s3_text_path, s3_image_path):
#             """
#             지정된 CSS Selectors에서 텍스트와 이미지를 탐지하여 최종 notice_type 값을 반환하고,
#             탐지된 이미지를 로컬 디렉토리에 다운로드하며 텍스트는 하나로 묶어 로컬에 저장.
#             """
#             all_image_urls = []  # 모든 섹션의 이미지 URL 저장
#             all_texts = []  # 모든 섹션의 텍스트 저장
#             final_notice_type = "none"  # 초기값 설정

#             for selector in div_selectors:
#                 try:
#                     # 섹션 가져오기
#                     section = driver.find_element(By.CSS_SELECTOR, selector)

#                     # 텍스트 탐지
#                     section_text = section.text.strip() if section.text else None
#                     if section_text:
#                         all_texts.append(section_text)

#                     # 이미지 탐지
#                     image_elements = section.find_elements(By.TAG_NAME, "img")
#                     section_image_urls = [img.get_attribute("src") for img in image_elements if img.get_attribute("src")]
#                     all_image_urls.extend(section_image_urls)
                    
#                     # notice_type 업데이트
#                     if section_text and section_image_urls:
#                         final_notice_type = "both"
#                     elif section_text and final_notice_type != "both":
#                         final_notice_type = "text"
#                     elif section_image_urls and final_notice_type not in ["both", "text"]:
#                         final_notice_type = "image"
#                 except Exception as e:
#                     print(f"CSS Selector {selector} 처리 중 에러 발생: {e}")

#             # 텍스트 파일 저장
#             combined_text = "\n".join(all_texts)
#             uploaded_text_path = upload_text_to_s3(s3_text_path, combined_text)

#             # 이미지 다운로드
#             uploaded_image_paths = upload_image_to_s3(s3_image_path, all_image_urls)

#             return final_notice_type, uploaded_image_paths, uploaded_text_path

#         def upload_text_to_s3(s3_text_path, texts):
#             """ 텍스트를 S3에 업로드하고 URL을 반환하는 함수 """
#             text_uuid = str(uuid.uuid4())  # UUID 생성
#             text_key = f"{s3_text_path}{text_uuid}.txt"  # S3에 저장할 경로 및 파일명
#             try:
#                 s3.put_object(Bucket=BUCKET_NAME, Key=text_key, Body=texts)
#                 text_url = f"s3://{BUCKET_NAME}/{text_key}"
#                 print(f"✅ 파일 {text_key}가 성공적으로 S3 {text_url}에 업데이트 되었습니다")
#                 return text_url
#             except Exception as e:
#                 print(f"⛔ [ERROR] Failed to upload text to S3: {e}")
#                 return None

#         def upload_image_to_s3(s3_image_path, image_urls):
#             """ 이미지 URL 리스트를 받아 이미지를 S3에 업로드하고 S3 URL 리스트를 반환하는 함수 """
#             s3_urls = []  # 업로드된 S3 URL을 저장할 리스트

#             for image_url in image_urls:
#                 try:
#                     # 이미지 다운로드
#                     response = requests.get(image_url, stream=True)
#                     response.raise_for_status()  # 다운로드 오류 시 예외 발생
#                     # UUID로 고유 이름 생성
#                     image_uuid = str(uuid.uuid4())
#                     image_key = f"{s3_image_path}{image_uuid}.jpg"
#                     # S3에 업로드
#                     s3.upload_fileobj(response.raw, BUCKET_NAME, image_key)
#                     # 업로드된 S3 URL 생성
#                     s3_url = f"s3://{BUCKET_NAME}/{image_key}"
#                     s3_urls.append(s3_url)

#                 except Exception as e:
#                     print(f"⛔ [ERROR] 이미지 업로드 실패 ({image_url}): {e}")

#             # 콤마로 연결된 S3 URL 반환
#             print(f"✅ 이미지 파일(들)이 성공적으로 S3 {s3_image_path}에 업데이트 되었습니다")
#             return s3_urls

#         def get_latest_txt_files(s3_link_path):
#             # 모든 파일 리스트 가져오기 (ContinuationToken 활용)
#             files = []
#             continuation_token = None
#             while True:
#                 params = {'Bucket': BUCKET_NAME, 'Prefix': s3_link_path}
#                 if continuation_token:
#                     params['ContinuationToken'] = continuation_token
#                 response = s3.list_objects_v2(**params)

#                 # s3 path 에 파일이 아예 없을 경우 처리
#                 if 'Contents' not in response:
#                     print(f"[ERROR] 해당 S3 path에 파일이 존재하지 않습니다: {s3_link_path}")
#                     return None
#                 # 파일 리스트에 추가
#                 files.extend(response['Contents'])

#                 # 다음 페이지로 넘어갈 ContinuationToken 확인
#                 continuation_token = response.get('NextContinuationToken')
#                 if not continuation_token:
#                     break
            
#             # txt 파일 리스트 가져오기
#             txt_files = [content['Key'] for content in files if content['Key'].endswith('.txt')]
#             if not txt_files:
#                 print("No .txt files found in the specified directory.")
#                 return []
            
#             # 파일명에서 날짜 추출 후 정렬
#             txt_files.sort(key=lambda x: datetime.strptime(x.split('/')[-1].split('.')[0], '%Y%m%d'))
#             # 최신 파일 1개 또는 2개 가져오기
#             latest_files = txt_files[-2:] if len(txt_files) > 1 else txt_files
#             # 최신 파일 2개의 내용 가져오기
#             file_contents = []
#             for file_key in latest_files:
#                 try:
#                     obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
#                     file_content = obj['Body'].read().decode('utf-8')
#                     file_contents.append(file_content)
#                 except Exception as e:
#                     print(f"[ERROR] 파일을 가져오는 중 오류가 발생했습니다. 파일 키: {file_key}, 에러: {e}")
#             return file_contents

#         def update_removed_links_in_db(removed_links, connection):
#             try:
#                 if not connection.open:
#                     connection.ping(reconnect=True)  # 연결이 닫혀있다면 재연결 시도
#                 for link in removed_links:
#                     sql = """
#                     UPDATE combined_table SET removed_time = %s WHERE org_url = %s AND site = 'rocketpunch'
#                     """
#                     cursor.execute(sql, (datetime.today().strftime("%Y-%m-%d"), link))
#                 connection.commit()
#                 print(f"Updated removed links in DB: {len(removed_links)}")
#             except Exception as e:
#                 print(f"Error updating removed links in DB: {e}")

#         # 메인 메소드
#         def main():
#             try:
#                 if not connection.open:
#                     print("❌ 데이터베이스 연결에 실패했습니다. 연결을 확인하세요.")
#                     return
                
#                 for job_abb, job_title in job_titles.items():
#                     s3_link_path = S3_LINK_PATH.format(abb = job_abb)
#                     s3_text_path = S3_TEXT_PATH.format(abb = job_abb) # s3 텍스트 저장 경로 설정
#                     s3_image_path = S3_IMAGE_PATH.format(abb = job_abb) # s3 이미지 저장 경로 설정

#                     # s3안에 어제 오늘 링크 가지고 오기
#                     latest_contents = get_latest_txt_files(s3_link_path)
#                     if len(latest_contents) == 0:
#                         print(f"{job_title}: You need to crawl the links first")

#                     elif len(latest_contents) == 1:
#                         # s3에 오늘 크롤링한 리스트만 있을때
#                         today_list = latest_contents[0].splitlines()
#                         for url in today_list:
#                             get_job_posts(url, job_title, s3_text_path, s3_image_path)
#                         print(f"[CHECKING] 오늘 크롤링한 공고의 개수: {len(today_list)}개")
#                     elif len(latest_contents) == 2:
#                         # "url1\nurl2\nurl3" 형식으로 나오므로 list로 변환
#                         yesterday_list = latest_contents[0].splitlines()
#                         today_list = latest_contents[-1].splitlines()
#                         print(f"{job_title}: {s3_link_path}로부터 오늘공고 {len(today_list)}개, 어제 공고 {len(yesterday_list)}개")

#                         # today_list에는 있지만 yesterday_list에는 없는 URL 리스트
#                         only_in_today = list(set(today_list) - set(yesterday_list))
#                         for url in only_in_today:
#                             get_job_posts(url, job_title, s3_text_path, s3_image_path)
#                         print(f"[CHECKING] 오늘 크롤링한 공고의 개수: {len(only_in_today)}개")

#                         # yesterday_list에는 있지만 today_list에는 없는 URL 리스트
#                         only_in_yesterday = list(set(yesterday_list) - set(today_list))
#                         update_removed_links_in_db(only_in_yesterday, connection)
#                     else:
#                         # 이론적으로는 len(latest_contents)가 0, 1, 2 이외의 값을 가질 수 없음
#                         print(f"{job_title}: Unexpected number of files found.")
                    
#                     # 그리고 저장된 path json으로 받아와서 db에 전부 업데이트 - dbmethod
#                     print(f"🌟{job_title}에 대한 크롤링과 DB업데이트를 완료하였습니다!")

#                 print("✅ 모든 데이터 삽입 및 업데이트가 성공했습니다!")
#             except Exception as e:
#                 print(f"Unexpected error during main execution: {e}")
#             finally:
#                 driver.quit()
#                 cursor.close()
#                 connection.close()
#         logging.info("로켓펀치 크롤링 완료")
#     except Exception as e:
#         logging.error(f"로켓펀치 크롤링 중 오류 발생: {e}")


def jobkorea_crawling():
    try:
        logging.info("잡코리아 크롤링 시작")
        # S3 버킷 이름 고정
        bucket_name = 't2jt'

        # AWS S3 연결 설정
        s3_client = boto3.client('s3')

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

        try:
            # AWS MySQL 연결 설정
            db = pymysql.connect(
                host='t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',  # AWS 퍼블릭 IP
                user='admin',  # MySQL 사용자
                password='dltkddn1',  # MySQL 비밀번호
                database='testdb1',  # 데이터베이스 이름
                port=3306,
                charset='utf8mb4'
            )

            # 커서 생성
            cursor = db.cursor()

            # 테이블에 데이터 삽입을 위한 SQL 쿼리
            insert_query = """
                INSERT INTO combined_table (create_time, update_time, removed_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url, responsibility, qualification, preferential)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # 작업 상태 기록 함수
            #def log_status(url, status, task_status):
            #    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #    logging.info(f"{url} - {status} - {task_status} - {time_now}")

            def log_status(url, status, task_status, additional_info=None):
                time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_message = f"{url} - {status} - {task_status} - {time_now}"
                if additional_info:
                    log_message += f" - {additional_info}"
                logging.info(log_message)

            # Selenium 웹 드라이버 설정
            #options = Options()
            #options.add_argument("--headless")
            #options.add_argument("--no-sandbox")
            #options.add_argument("--disable-dev-shm-usage")
            #options.add_argument("--disable-gpu")
            # options.add_argument('--disable-software-rasterizer')  # 소프트웨어 렌더링 비활성화
            # options.add_argument("--remote-debugging-port=9222")
            # options.add_argument("--window-size=1920x1080")
            # options.add_argument("--disable-background-networking")
            # options.add_argument("--disable-renderer-backgrounding")
            # options.add_argument("--disable-background-timer-throttling")
            # options.add_argument("--disable-extensions")
            # options.add_argument("--disable-infobars")
            #options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36")

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument('--disable-software-rasterizer')  # 소프트웨어 렌더링 비활성화
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")


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

            # log.txt 파일 읽기
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
                        
#                        # 로드된 페이지의 URL 확인
#                        current_url = driver.current_url
#                        if current_url != url:
#                            log_status(url, "redirected", "failed", additional_info=f"Redirected to {current_url}")
#                            print(f"[WARNING] URL 리디렉션 감지: {url} -> {current_url}")
#                            continue  # 리디렉션된 경우 현재 URL 작업 건너뜀
#
#                        # CAPTCHA 또는 차단 페이지 감지
#                        if "captcha" in driver.page_source.lower() or "차단되었습니다" in driver.page_source:
#                            log_status(url, "captcha_detected", "failed", additional_info="CAPTCHA or block detected")
#                            print(f"[ERROR] CAPTCHA 또는 차단 페이지 감지: {url}")
#                            continue
#
#                        # 페이지가 완전히 로드될 때까지 대기
#                        WebDriverWait(driver, 20).until(
#                            lambda driver: driver.execute_script("return document.readyState") == "complete")

                        # iframe 전환
                        try:
                            iframe = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#gib_frame"))
                            )
                            driver.switch_to.frame(iframe)
                            logging.info(f"[INFO] iframe 전환 성공: {url}")
#                        except Exception as e:
#                            log_status(url, "iframe_switch", "failed", additional_info=str(e))
#                            print(f"[ERROR] iframe 전환 실패: {url}, 에러: {e}")
#                            continue  # 다음 URL로 이동

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
                        #log_status(url, "update", f"failed - {e}")  # 에러 메시지 로그 추가
                        log_status(url, "update", "failed", additional_info=str(e))
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
        except Exception as e:
            logging.critical(f"전체 작업 실패: {e}", exc_info=True)

        finally:
            # 웹 드라이버 종료
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"웹 드라이버 종료 실패: {e}", exc_info=True)

            # MySQL 연결 끊기
            try:
                db.close()
            except Exception as e:
                logging.error(f"MySQL 연결 종료 실패: {e}", exc_info=True)

            # 처리 결과 출력
            print(f"[INFO] 처리된 총 개수: {processed_count}")
            print(f"[INFO] 오류 개수: {error_count}")
            for error_type, count in error_types.items():
                print(f"[INFO] {error_type}: {count}")

        logging.info("잡코리아 크롤링 완료")
    except Exception as e:
        logging.error(f"잡코리아 크롤링 중 오류 발생: {e}")


def saramin_crawling():
    try:
        # AWS S3 클라이언트 생성
        s3 = boto3.client('s3')

        # S3 설정 - 기본값
        BUCKET_NAME = "t2jt"
        DEFAULT_KEYWORD = "DE"  # 기본 키워드
        S3_BASE_PATH = f"job/{DEFAULT_KEYWORD}/sources/saramin/links"
        S3_TEXT_PATH = f"job/{DEFAULT_KEYWORD}/sources/saramin/txt"
        S3_IMAGES_PATH = f"job/{DEFAULT_KEYWORD}/sources/saramin/images"

        # 오늘과 어제 날짜 파일 경로를 동적으로 생성할 함수
        def get_s3_paths(keyword):
            base_path = f"job/{keyword}/sources/saramin/links"
            text_path = f"job/{keyword}/sources/saramin/txt"
            images_path = f"job/{keyword}/sources/saramin/images"
            today_file = f"{base_path}/{datetime.now().strftime('%Y%m%d')}.txt"
            yesterday_file = f"{base_path}/{(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')}.txt"
            return base_path, text_path, images_path, today_file, yesterday_file

        # MySQL 연결 풀 설정
        db_config = {
            'host': 't2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',
            'user': 'admin',
            'password': 'dltkddn1',
            'database': 'testdb1',
            'port': '3306'
        }

        # Mysql 연결 재사용 연결 풀링 설정
        connection_pool = pooling.MySQLConnectionPool(pool_name="testdb1_pool", pool_size=5, **db_config)

        def get_connection():
            return connection_pool.get_connection()

        # S3에 텍스트 업로드
        def upload_to_s3(content, file_name):
            try:
                s3.put_object(Bucket=BUCKET_NAME, Key=f"{S3_TEXT_PATH}/{file_name}", Body=content)
                s3_url = f"s3://{BUCKET_NAME}/{S3_TEXT_PATH}/{file_name}"
                logging.info(f"S3에 텍스트 업로드 성공: {s3_url}")
                return s3_url
            except Exception as e:
                logging.error(f"S3 업로드 실패: {e}")
                return None
            
        # S3 파일 읽기 함수 (재시도 포함)
        def read_s3_file(bucket, path, retries=3):
            for attempt in range(retries):
                try:
                    logging.info(f"[INFO] S3 파일 읽기 시도: Bucket={bucket}, Path={path}")
                    response = s3.get_object(Bucket=bucket, Key=path)
                    file_content = response['Body'].read().decode('utf-8').strip()

                    if not file_content:
                        logging.warning(f"[WARNING] S3 파일 내용이 비어 있습니다: {path}")
                        return ""

                    return file_content
                except Exception as e:
                    logging.error(f"[ERROR] S3 파일 읽기 실패 (시도 {attempt + 1}/{retries}): {e}")
                    if attempt < retries - 1:
                        time.sleep(2)  # 재시도 전 대기
                    else:
                        return ""

        # URL 추출 함수
        def extract_urls_with_details(content):
            """
            Extract URLs along with JOB_TITLE, COMPANY, and POST_TITLE from content.
            Normalize URLs for consistent comparison.
            """
            data = []
            for line in content.splitlines():
                url_match = re.search(r"ORG_URL:\s*(https?://[^\s,]+)", line)
                job_title_match = re.search(r"JOB_TITLE:\s*([^,]+)", line)
                company_match = re.search(r"COMPANY:\s*([^,]+)", line)
                post_title_match = re.search(r"POST_TITLE:\s*([^,]+)", line)

                if url_match:
                    url = normalize_url(url_match.group(1).strip())  # URL 정규화
                    job_title = job_title_match.group(1).strip() if job_title_match else "Unknown Job Title"
                    company = company_match.group(1).strip() if company_match else "Unknown Company"
                    post_title = post_title_match.group(1).strip() if post_title_match else "Unknown Post Title"
                    data.append((url, job_title, company, post_title))
            return data

        # DB 중복 URL 확인 함수
        def is_url_in_db(org_url):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM combined_table WHERE org_url = %s AND site = 'saramin'", (org_url,))
                return cursor.fetchone()[0] > 0
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        # MySQL 데이터베이스에 배치 삽입
        def batch_insert_to_db(data):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                insert_query = """
                    INSERT INTO combined_table (
                        id, create_time, update_time, removed_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                # 데이터 내의 notice_type 값을 설정하여 새로운 리스트 생성
                updated_data = []
                for record in data:
                    record = list(record)  # 튜플을 리스트로 변환
                    s3_text_url = record[12]  # s3_text_url 위치
                    s3_images_url = record[13]  # s3_images_url 위치

                    # notice_type 결정
                    if s3_text_url and not s3_images_url:
                        notice_type = "text"
                    elif not s3_text_url and s3_images_url:
                        notice_type = "images"
                    elif s3_text_url and s3_images_url:
                        notice_type = "both"
                    else:
                        notice_type = "none"

                    # notice_type 업데이트
                    record[10] = notice_type  # notice_type 위치
                    updated_data.append(tuple(record))  # 리스트를 다시 튜플로 변환

                # 업데이트된 데이터를 DB에 삽입
                cursor.executemany(insert_query, updated_data)
                conn.commit()
                logging.info(f"{len(updated_data)}개의 데이터가 성공적으로 삽입되었습니다.")
            except Exception as e:
                logging.error(f"배치 삽입 실패: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        # DB에서 removed_time 업데이트
        def update_removed_time(org_url):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                removed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE combined_table SET removed_time = %s WHERE org_url = %s AND site = 'saramin'", (removed_time, org_url))
                conn.commit()
                logging.info(f"DB 업데이트 완료: org_url = {org_url}, removed_time = {removed_time}")
            except Exception as e:
                logging.error(f"DB 업데이트 실패: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()

        # 이미지 URL을 다운로드하여 S3에 저장한 후, DB에 저장할 URL을 반환
        def upload_image_to_s3(image_url):
            try:
                # S3 키로 사용하기 위해 URL의 슬래시를 |로 인코딩
                encoded_url = image_url.replace('/', '|')  # 슬래시를 %2F로 변환
                s3_key = f"{S3_IMAGES_PATH}/{encoded_url}"

                # 원본 URL에서 이미지 다운로드
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    # S3에 이미지 업로드
                    s3.put_object(
                        Bucket=BUCKET_NAME,
                        Key=s3_key,
                        Body=response.content,
                        ContentType=response.headers.get('Content-Type', 'application/octet-stream')
                    )
                    # DB에 저장할 S3 경로와 원본 URL 결합
                    s3_db_entry = f"s3://{BUCKET_NAME}/{s3_key}"
                    logging.info(f"S3 업로드 성공 및 DB 경로 생성: {s3_db_entry}")
                    return s3_db_entry  # S3 경로 반환
                else:
                    logging.error(f"이미지 다운로드 실패: {image_url}, 상태 코드: {response.status_code}")
                    return None
            except Exception as e:
                logging.error(f"이미지 업로드 실패: {image_url}, 에러: {e}")
                return None

        # 마감일과 텍스트 또는 이미지 가져오기
        def extract_due_date_and_content(url, next_id, job_title, company, post_title, retries=3):
            s3_text_url = None
            s3_images_url = None

            for attempt in range(retries):
                try:
                    logging.info(f"URL로 이동 중 (시도 {attempt + 1}/{retries}): {url}")

                    chrome_options = Options()
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-gpu")
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")  # User-Agent 설정

                    driver = webdriver.Chrome(options=chrome_options)
                    driver.get(url)

                    time.sleep(10)

                    # iframe 전환
                    try:
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "iframe_content_0")))
                        iframe = driver.find_element(By.ID, "iframe_content_0")
                        driver.switch_to.frame(iframe)
                    except Exception as e:
                        logging.error(f"iframe 탐색 실패: {e}")
                        return False

                    # user_content 탐색
                    try:
                        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "user_content")))
                        content_element = driver.find_element(By.CLASS_NAME, "user_content")
                        extracted_text = content_element.text.strip()
                        logging.info(f"추출된 텍스트: {extracted_text}")
                    except Exception as e:
                        logging.error(f"user_content 탐색 실패: {e}")
                        return False

                    # 텍스트 처리 - S3 저장
                    if extracted_text:
                        file_name = f"{uuid.uuid4()}.txt"
                        s3_key = f"{S3_TEXT_PATH}/{file_name}"
                        s3.put_object(Bucket=BUCKET_NAME, Key=s3_key, Body=extracted_text.encode("utf-8"))
                        s3_text_url = f"s3://{BUCKET_NAME}/{s3_key}"
                        logging.info(f"S3에 텍스트 저장 완료: {s3_text_url}")

                        # 텍스트가 있으면 이미지는 건너뛴다
                        s3_images_url = None
                    else:
                        # 이미지 URL 추출 및 S3 업로드
                        user_content = driver.find_element(By.CLASS_NAME, "user_content")
                        img_elements = user_content.find_elements(By.TAG_NAME, "img")
                        images_urls = {img.get_attribute("src").strip() for img in img_elements if img.get_attribute("src")}

                        if images_urls:
                            # 각 이미지를 S3에 업로드하고 S3 경로 수집
                            uploaded_urls = [upload_image_to_s3(image_url) for image_url in images_urls]
                            s3_images_url = ", ".join(filter(None, uploaded_urls))  # None 값 제거

                    # 마감일 추출
                    driver.switch_to.default_content()
                    title_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "title")))
                    title_text = title_element.get_attribute("textContent").strip()

                    match = re.search(r"\(([^()]*)\)\s*- 사람인", title_text)
                    if match:
                        due_date_value = match.group(1).strip()
                        if "D-" in due_date_value:
                            days_to_add = int(due_date_value.split("-")[1])
                            due_date = (datetime.now() + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
                            due_type = "날짜"
                        else:
                            due_date = None
                            due_type = due_date_value  # D-가 아닌 경우 원문 반환
                    else:
                        due_date_value, due_date, due_type = "없음", None, "없음"

                    # notice_type 결정
                    if s3_text_url and not s3_images_url:
                        notice_type = "text"
                    elif not s3_text_url and s3_images_url:
                        notice_type = "images"
                    elif s3_text_url and s3_images_url:
                        notice_type = "both"
                    else:
                        notice_type = "none"

                    # DB 저장
                    save_to_db(
                        next_id=next_id,
                        job_title=job_title,
                        company=company,
                        post_title=post_title,
                        due_type=due_type,
                        due_date=due_date,
                        notice_type=notice_type,
                        url=url,
                        s3_text_url=s3_text_url,
                        s3_images_url=s3_images_url
                    )
                    return True

                except Exception as e:
                    logging.error(f"마감일 및 콘텐츠 추출 실패 (시도 {attempt + 1}/{retries}): {e}")
                    if attempt < retries - 1:
                        logging.info("재시도 중...")
                        time.sleep(5)  # 재시도 전에 대기
                    else:
                        logging.error("최대 재시도 횟수에 도달했습니다.")
                        return False
                finally:
                    driver.quit()

        # DB 저장 함수
        def save_to_db(next_id, job_title, company, post_title, due_type, due_date, notice_type, url, s3_text_url, s3_images_url):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                insert_query = """
                    INSERT INTO combined_table (
                        id, create_time, update_time, removed_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    next_id,
                    datetime.now(),
                    datetime.now(),
                    None,
                    "saramin",
                    job_title,
                    due_type,
                    due_date,
                    company,
                    post_title,
                    notice_type,
                    url,
                    s3_text_url,
                    s3_images_url
                ))
                conn.commit()
                logging.info(f"DB에 저장 성공 - URL: {url}, Job Title: {job_title}, Company: {company}, Post_Title: {post_title}, S3 Text URL: {s3_text_url}, S3 Images URL: {s3_images_url}")
            except Exception as e:
                logging.error(f"DB 저장 실패 - URL: {url}, Error: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()


        # 정규화된 URL 사용 (URL을 정규화로 비교 가능 형태로 변환)
        def normalize_url(url):
            try:
                parsed_url = urlparse(url)
                query_params = sorted(parse_qsl(parsed_url.query), key=lambda x: x[0])  # 정렬된 쿼리
                normalized_query = urlencode(query_params, doseq=True)
                normalized_url = parsed_url._replace(
                    scheme=parsed_url.scheme.lower(),
                    netloc=parsed_url.netloc.lower(),
                    query=normalized_query,
                    fragment=''  # 불필요한 fragment 제거
                ).geturl()
                logging.debug(f"URL 정규화 완료: {url} -> {normalized_url}")
                return normalized_url
            except Exception as e:
                logging.error(f"URL 정규화 실패: {url}, 에러: {e}")
                return url
        # 실행 로직
        # 오늘날짜.txt와 DB와 먼저 중복 체크 후 오늘날짜.txt와 어제날짜.txt비교 후 추가 및 제거
        def execute(keyword):
            try:
                # 동적으로 S3 경로 설정
                global S3_BASE_PATH, S3_TEXT_PATH, S3_IMAGES_PATH, today_file_path, yesterday_file_path
                S3_BASE_PATH, S3_TEXT_PATH, S3_IMAGES_PATH, today_file_path, yesterday_file_path = get_s3_paths(keyword)

                # S3 파일 읽기
                today_content = read_s3_file(BUCKET_NAME, today_file_path)
                yesterday_content = read_s3_file(BUCKET_NAME, yesterday_file_path)

                if not today_content:
                    logging.warning(f"{keyword}: 오늘 파일을 읽을 수 없어 작업을 건너뜁니다.")
                    return

                if not yesterday_content:
                    logging.info(f"{keyword}: 어제 파일이 비어 있거나 존재하지 않습니다. 어제 데이터를 비어 있는 것으로 간주합니다.")
                    yesterday_content = ""  # 어제 데이터를 빈 값으로 설정

                # 오늘 날짜 파일에서 URL 및 관련 데이터 추출
                today_data = extract_urls_with_details(today_content)
                yesterday_data = extract_urls_with_details(yesterday_content)  # 어제 파일
                logging.info(f"[{keyword}] 오늘 날짜 파일에서 추출된 데이터: {len(today_data)}개")
                logging.info(f"[{keyword}] 어제 날짜 파일에서 추출된 데이터: {len(yesterday_data)}개")

                # DB와 중복 확인
                filtered_today_data = []
                conn = get_connection()
                try:
                    cursor = conn.cursor()
                    for url, job_title, company, post_title in today_data:
                        cursor.execute("SELECT COUNT(*) FROM combined_table WHERE org_url = %s AND site = 'saramin'", (url,))
                        if cursor.fetchone()[0] == 0:  # DB에 없는 경우만 추가
                            filtered_today_data.append((url, job_title, company, post_title))
                    logging.info(f"[{keyword}] DB 중복 확인 후 남은 데이터: {len(filtered_today_data)}개")
                finally:
                    if conn.is_connected():
                        cursor.close()
                        conn.close()

                # 어제 날짜 파일에서 URL 데이터 추출
                yesterday_urls = {normalize_url(item[0]) for item in yesterday_data} if yesterday_content else set()
                today_urls = {normalize_url(data[0]) for data in today_data}

                # 추가 및 제거된 URL 계산
                added_urls = today_urls - yesterday_urls
                removed_urls = yesterday_urls - today_urls

                # added_data 생성
                added_data = [data for data in filtered_today_data if normalize_url(data[0]) in added_urls]


                # 디버깅용 추가 및 제거된 URL 로깅
                logging.debug(f"[{keyword}] 추가된 URL 개수: {len(added_data)}, 목록: {[data[0] for data in added_data]}")
                logging.debug(f"[{keyword}] 제거된 URL 개수: {len(removed_urls)}, 목록: {list(removed_urls)}")
                logging.info(f"추가된 URL: {len(added_data)}개")
                logging.info(f"제거된 URL: {len(removed_urls)}개")

                # DB에서 ID 초기화
                conn = get_connection()
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(id) FROM combined_table")
                    max_id_result = cursor.fetchone()[0]
                    next_id = (max_id_result + 1) if max_id_result is not None else 1  # 없는 경우 1로 시작
                finally:
                    if conn.is_connected():
                        cursor.close()
                        conn.close()

                # 추가된 데이터 처리
                for url, job_title, company, post_title in added_data:
                    if extract_due_date_and_content(url, next_id, job_title, company, post_title):
                        next_id += 1

                # 제거된 데이터 처리
                for org_url in removed_urls:
                    update_removed_time(org_url)
                    logging.info(f"제거된 데이터 업데이트 완료: {org_url}")

                logging.info("모든 작업이 완료되었습니다.")

            except Exception as e:
                logging.error(f"실행 중 오류 발생: {e}")

        def execute_for_all_keywords():
            """
            모든 키워드에 대해 작업 실행.
            """
            KEYWORDS = ["DE", "FE", "BE", "DA", "MLE"]

            for keyword in KEYWORDS:
                logging.info(f"=== {keyword} 작업 시작 ===")
                execute(keyword)
                logging.info(f"=== {keyword} 작업 완료 ===")
        execute_for_all_keywords()
        logging.info("사람인 크롤링 완료")
    except Exception as e:
        logging.error(f"사람인 크롤링 중 오류 발생: {e}")


def post_main():
    kill_existing_chrome()  # 기존 프로세스 강제 종료
    
    logging.info(f"점핏 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    #jumpit_crawling()
    logging.info(f"점핏 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    logging.info(f"원티드 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    wanted_crawling()
    logging.info(f"원티드 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    logging.info(f"인크루트 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    #incruit_crawling()
    logging.info(f"인크루트 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    logging.info(f"로켓펀치 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    #rocketpunch_crawling()
    logging.info(f"로켓펀치 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    logging.info(f"잡코리아 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    jobkorea_crawling()
    logging.info(f"잡코리아 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    logging.info(f"사람인 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    saramin_crawling()
    logging.info(f"사람인 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

if __name__ == "__main__":
    post_main()

