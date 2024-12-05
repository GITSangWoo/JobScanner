import os
import time
import requests
import uuid
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import re
from mysql.connector import pooling
from io import StringIO

# MySQL 연결 풀 설정
db_config = {
    'user': 'user',
    'password': '1234',
    'host': '43.201.40.223',
    'database': 'testdb',
    'port': 3306
}

connection_pool = pooling.MySQLConnectionPool(pool_name="incruit_pool", pool_size=5, **db_config)

def insert_into_db(data):
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        sql = """
        INSERT INTO incruit (site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url, create_time, update_time) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['site'], data['job_title'], data['due_type'], data['due_date'], data['company'],
            data['post_title'], data['notice_type'], data['org_url'], data['s3_text_url'], data['s3_image_url'], 
            data['create_time'], data['update_time']
        )
        cursor.execute(sql, values)
        connection.commit()
        print(f"Data inserted into DB: {data['post_title']}")

    except Exception as e:
        print(f"Error inserting data into DB: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def update_removed_links_in_db(removed_links):
    try:
        connection = connection_pool.get_connection()
        cursor = connection.cursor()

        for link in removed_links:
            print(f"URL {link} is marked as deleted. Checking if it exists in the database.")
            
            # Check if URL exists in DB
            cursor.execute("SELECT 1 FROM incruit WHERE org_url = %s", (link,))
            result = cursor.fetchone()
            if not result:
                print(f"URL {link} not found in DB, skipping removed_time update.")
                continue

            # Update removed_time without checking done_time
            removed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            update_time_query = """
            UPDATE incruit
            SET removed_time = %s
            WHERE org_url = %s
            """
            cursor.execute(update_time_query, (removed_time, link))

            # Check if update was successful
            if cursor.rowcount == 0:
                print(f"No rows updated for URL: {link}")
            else:
                print(f"Removed time updated for URL: {link}")
        
        connection.commit()
        print(f"Updated removed links in DB: {len(removed_links)}")

    except Exception as e:
        print(f"Error updating removed links in DB: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()


def upload_to_s3(content, bucket_name, object_name):
    try:
        s3 = boto3.client('s3')
        
        # 만약 content가 문자열이면, 이를 바이트로 인코딩
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # S3에 업로드
        s3.put_object(Bucket=bucket_name, Key=object_name, Body=content)
        print(f"Uploaded to S3 as {object_name}")
        return f"s3://{bucket_name}/{object_name}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

def download_from_s3_direct(s3_uri):
    try:
        s3_uri_parts = s3_uri.replace("s3://", "").split("/", 1)
        bucket_name = s3_uri_parts[0]
        object_name = s3_uri_parts[1]

        s3_client = boto3.client('s3')
        obj = s3_client.get_object(Bucket=bucket_name, Key=object_name)
        file_content = obj['Body'].read().decode('utf-8')

        print(f"Successfully read from S3: {s3_uri}")
        return file_content
    except Exception as e:
        print(f"Error reading from S3: {e}")
        return None

def process_images(image_urls, job_id, img_folder, bucket_name, s3_folder):
    s3_image_urls = []
    for i, img_url in enumerate(image_urls):
        try:
            img_filename = f"{job_id}_image_{i + 1}.jpg"
            # 이미지를 로컬에 저장하지 않고 직접 메모리로 처리
            img_url_data = requests.get(img_url).content
            s3_image_url = upload_to_s3(img_url_data, bucket_name, f"{s3_folder}/{img_filename}")
            if s3_image_url:
                s3_image_urls.append(s3_image_url)
        except Exception as e:
            print(f"Error processing image {img_url}: {e}")
    return s3_image_urls

def convert_to_mysql_date(due_date):
    match = re.match(r'(\d{4})\.(\d{2})\.(\d{2})', due_date)
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}" if match else None

# 크롤링 타임아웃을 위한 기본 설정
CRAWL_TIMEOUT = 30  # 30초로 설정

# Chrome 설정
options = Options()
options.headless = False
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 오늘 날짜로 로그파일 이름 설정
output_folder = "incruit"
today = datetime.today().strftime('%Y%m%d')
log_file_name = os.path.join(output_folder, f"{today}.log")  # 로컬 파일 사용

# DB 연결을 크롤링 시작 전에 한 번만 열고, 크롤링이 다 끝난 후 connection.close() 호출
connection = connection_pool.get_connection()

# 기존 로그 파일을 읽고, "update" 상태인 URL들만 크롤링
def update_log_file(url, crawl_time):
    # 로그 파일을 읽고, 해당 URL의 상태 업데이트
    with open(log_file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 새로운 데이터를 담을 리스트
    updated_lines = []
    
    for line in lines:
        columns = line.strip().split(',')
        if columns[1] == url:
            # URL이 일치하면 work_status를 "done"으로 업데이트하고, done_time 추가
            columns[2] = "done"
            columns[3] = crawl_time
            columns[0] = job_title
            updated_line = ','.join(columns)
            updated_lines.append(updated_line + '\n')
        else:
            # 일치하지 않으면 기존 라인을 그대로 추가
            updated_lines.append(line)
    
    # 로그 파일을 덮어쓰기 (한 줄씩 업데이트)
    with open(log_file_name, 'w', encoding='utf-8') as file:
        file.writelines(updated_lines)

# 기존 로그 파일을 읽고, "update" 상태인 URL들만 크롤링
with open(log_file_name, 'r', encoding='utf-8') as file:
    lines = file.readlines()

    # 'update' 상태인 URL들을 크롤링 대상 리스트에 추가
    removed_links = []

    for line in lines[1:]:
        columns = line.strip().split(',')
        job_title = columns[0]  # job_title 추출
        url = columns[1]        # URL 추출
        notice_status = columns[2]
        work_status = columns[3]
        done_time = columns[4] if len(columns) > 4 else None

        if notice_status == "update" and work_status == "null":
            print(f"Starting crawl for {job_title}: {url}")
            # 크롤링 작업 수행
            crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            try:
                # 각 링크에 대해 로딩 타임아웃 설정
                driver.get(url)
                driver.set_page_load_timeout(CRAWL_TIMEOUT)  # 페이지 로딩 타임아웃 설정
                time.sleep(3)

                company = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job_info_detail .top-cnt a"))
                ).text.strip()
                post_title = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job_info_detail .top-cnt h1"))
                ).text.strip()

                # 마감 날짜 추출
                due_type, due_date_mysql = "NULL", None
                try:
                    reception_section = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".reception"))
                    )
                    deadline_elements = reception_section.find_elements(By.CSS_SELECTOR, ".intxt.end .day em")
                    if deadline_elements:
                        due_type = "날짜"
                        due_date_mysql = convert_to_mysql_date(deadline_elements[0].text.strip())
                    else:
                        status_elements = reception_section.find_elements(By.CSS_SELECTOR, ".d_day.pts")
                        due_type = status_elements[0].text.strip() if status_elements else "NULL"
                except Exception as e:
                    print(f"Error extracting deadline: {e}")

                iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ifrmJobCont")))
                driver.switch_to.frame(iframe)
                content_job_section = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "content_job")))

                text_content = content_job_section.text.strip()
                image_urls = [img.get_attribute("src") for img in content_job_section.find_elements(By.TAG_NAME, "img")]
                driver.switch_to.default_content()

                job_id = str(uuid.uuid4())
                text_filename = f"{job_id}.txt"
                s3_text_url = upload_to_s3(text_content, "t2jt", f"job/{job_title}/sources/incruit/txt/{job_id}.txt")

                s3_image_urls = process_images(image_urls, job_id, "./images", "t2jt", f"job/{job_title}/sources/incruit/images")

                notice_type = "both" if s3_text_url and s3_image_urls else "text" if s3_text_url else "images" if s3_image_urls else "NULL"

                insert_into_db({
                    "site": "incruit",
                    "job_title": job_title,
                    "due_type": due_type,
                    "due_date": due_date_mysql,
                    "company": company,
                    "post_title": post_title,
                    "notice_type": notice_type,
                    "org_url": url,
                    "s3_text_url": s3_text_url,
                    "s3_image_url": ";".join(s3_image_urls),
                    "create_time": datetime.now(),
                    "update_time": datetime.now(),
                })

                # 작업 완료 후 로그 파일 업데이트
                update_log_file(url, crawl_time)

            except Exception as e:
                print(f"Error processing {job_title} - {url}: {e}")

        elif notice_status == "deleted" and work_status == "done":
            removed_links.append(url)

    if removed_links:
        update_removed_links_in_db(removed_links)

# 크롤링 완료 후 DB 연결 종료
connection.close()

driver.quit()
