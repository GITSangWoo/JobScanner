import os
import time
import uuid
import boto3
import pymysql
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# AWS S3 클라이언트 설정
s3_client = boto3.client('s3')

# MySQL 연결 설정
connection = pymysql.connect(
    host='43.201.40.223',
    user='user',
    password='1234',
    database='testdb',
    port=3306
)
cursor = connection.cursor()

# S3 버킷과 폴더 경로 설정
s3_bucket_name = 't2jt'
s3_folder_path = 'job/DE/sources/wanted/txt/'

# 셀레니움 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 오늘 날짜로 로그파일 이름 설정
today = datetime.today().strftime('%Y%m%d')
log_file_name = f"{today}.log"
error_log_file_name = f"{today}_error.log"  # 에러 로그 파일

# 크롤링한 콘텐츠를 로컬에 저장하고, S3에 업로드 후 URL 반환
def save_crawled_content(url, content):
    file_name = f"{uuid.uuid4()}.txt"  # UUID로 파일 이름 생성
    file_path = os.path.join('textnotice', file_name)
    
    # 로컬에 저장
    if not os.path.exists('textnotice'):
        os.makedirs('textnotice')
    
    # 크롤링한 내용을 로컬 파일에 저장
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Content saved locally to {file_path}")
    
    # S3에 파일 업로드
    s3_file_path = os.path.join(s3_folder_path, file_name)
    try:
        s3_client.put_object(
            Bucket=s3_bucket_name,
            Key=s3_file_path,  # 'job/DE/sources/wanted/txt/UUID.txt'
            Body=content,
            ContentType='text/plain'
        )
        s3_url = f"s3://{s3_bucket_name}/{s3_file_path}"
        print(f"Content uploaded to S3 at {s3_url}")
        return s3_url  # S3 URL 반환
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        
        # S3 업로드 오류를 에러 로그 파일에 기록
        error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(error_log_file_name, 'a', encoding='utf-8') as error_log:
            error_log.write(f"{error_time}, {url}, S3 upload error: {str(e)}\n")
        
        return None

# 페이지 크롤링 함수
def crawl_url(url, job_title):
    driver.get(url)
    time.sleep(3)  # 페이지 로딩 대기
    
    try:
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
        s3_text_url = save_crawled_content(url, job_content_text)
        
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
        INSERT INTO wanted (create_time, update_time, removed_time, site, job_title, due_type, due_date, company, 
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
        print(f"Error during crawling {url}: {e}")
        
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
        cursor.execute("SELECT removed_time FROM wanted WHERE org_url = %s", (url,))
        result = cursor.fetchone()

        if result:
            removed_time = done_time  # 로그에서 가져온 done_time 값을 removed_time으로 사용
            print(f"URL {url} exists in DB. Updating removed_time to: {removed_time}")
            # 데이터베이스에서 removed_time을 done_time으로 업데이트
            update_time_query = """
            UPDATE wanted
            SET removed_time = %s
            WHERE org_url = %s
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
