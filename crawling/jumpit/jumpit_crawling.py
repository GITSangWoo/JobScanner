import os
import time
import uuid
import boto3
import pymysql
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
from webdriver_manager.chrome import ChromeDriverManager
import re

output_folder = "jumpit"
today = datetime.today().strftime('%Y%m%d')
log_file_name = os.path.join(output_folder, f"{today}.log")

def save_crawled_content(url, content):
    file_name = url.split('/')[-1] + ".txt"
    file_path = os.path.join('textnotice', file_name)
    
    if not os.path.exists('textnotice'):
        os.makedirs('textnotice')
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"Content saved to {file_path}")

def insert_into_db(data, connection): 
    with connection.cursor() as cursor:
        sql = """
        INSERT INTO jumpit (site, job_title, due_type, due_date, company, post_title, org_url, s3_text_url, notice_type, create_time, update_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            data['site'], data['job_title'], data['due_type'], data['due_date'], data['company'],
            data['post_title'], data['org_url'], data['s3_text_url'], data['notice_type'],
            data['create_time'], data['update_time']
        ))
        connection.commit()

def update_removed_links_in_db(removed_links, connection):
    try:
        with connection.cursor() as cursor:
            for link in removed_links:
                sql = """
                UPDATE jumpit SET removed_time = %s WHERE org_url = %s
                """
                cursor.execute(sql, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), link))
            connection.commit()
            print(f"Updated removed links in DB: {len(removed_links)}")
    except Exception as e:
        print(f"Error updating removed links in DB: {e}")

def read_links_and_ddays_from_s3(bucket_name, s3_file_key):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=s3_file_key)
        content = response['Body'].read().decode('utf-8')
        
        links_with_ddays = {}
        for line in content.splitlines():
            if ": " in line:
                link, d_day = line.strip().split(": ", 1)
                link = re.sub(r':\s*\d+$', '', link)
                
                try:
                    d_day_int = int(d_day)
                    links_with_ddays[link] = d_day_int
                except ValueError:
                    print(f"Invalid D-day value: {d_day} for URL: {link}")
        
        return links_with_ddays
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        return {}

def upload_to_s3(file_path, bucket_name, object_name):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f"Uploaded {file_path} to S3 bucket {bucket_name} as {object_name}")
        return f"s3://{bucket_name}/{object_name}"
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return None

def extract_site_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.hostname
    return domain.split('.')[0] if domain else None

def calculate_deadline_from_dday(d_day):
    today = datetime.now().date()
    deadline = today + timedelta(days=d_day)
    return deadline

def update_log_file(url, crawl_time):
    with open(log_file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    updated_lines = []
    
    for line in lines:
        columns = line.strip().split(',')
        if columns[1] == url:
            job_title = columns[0].strip()  # 로그 파일에서 job_title 추출
            columns[2] = "done"
            columns[3] = crawl_time
            updated_line = ','.join(columns)
            updated_lines.append(updated_line + '\n')
        else:
            updated_lines.append(line)
    
    with open(log_file_name, 'w', encoding='utf-8') as file:
        file.writelines(updated_lines)


bucket_name = 't2jt'
today_file_key = f"job/DE/sources/jumpit/links/{today}.txt"  # 기본값은 DE로 설정

links_with_ddays = read_links_and_ddays_from_s3(bucket_name, today_file_key)

urls_to_crawl = list(links_with_ddays.keys())

connection = pymysql.connect(
    host='43.201.40.223',
    user='user',
    password='1234',
    database='testdb',
    port=3306
)

options = Options()
options.headless = False
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

with open(log_file_name, 'r', encoding='utf-8') as file:
    lines = file.readlines()

removed_links = []

for line in lines[1:]:  # 헤더는 제외
    columns = line.strip().split(',')
    job_title = columns[0].strip()  # 로그 파일에서 job_title 추출
  # 로그에서 직무명을 추출
    url = columns[1]
    notice_status = columns[2]
    work_status = columns[3]
    done_time = columns[4]
    d_day = columns[5]

    try:
        with connection.cursor() as cursor:
            if notice_status == "deleted" and work_status == "done":
                print(f"URL {url} is marked as deleted. Checking if it exists in the database.")
                
                # Check if URL exists in DB
                cursor.execute("SELECT 1 FROM jumpit WHERE org_url = %s", (url,))
                result = cursor.fetchone()
                if not result:
                    print(f"URL {url} not found in DB, skipping removed_time update.")
                    continue

                # Update removed_time without checking done_time
                removed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                update_time_query = """
                UPDATE jumpit
                SET removed_time = %s
                WHERE org_url = %s
                """
                cursor.execute(update_time_query, (removed_time, url))
                
                # Check if update was successful
                if cursor.rowcount == 0:
                    print(f"No rows updated for URL: {url}")
                else:
                    print(f"Removed time updated for URL: {url}")
                connection.commit()

            elif notice_status == "update" and work_status == "null":
                print(f"Starting crawl for {url}")
                crawl_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                driver.get(url)
                time.sleep(3)
                
                job_content_text = None
                try:
                    job_content_section = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-10492dab-3.hiVlDL"))
                    )
                    job_content_text = job_content_section.text
                except Exception:
                    print(f"Failed to extract job content from {url}")
                
                if job_content_text:
                    text_path = os.path.join("texts", f"{uuid.uuid4()}.txt")
                    with open(text_path, "w", encoding="utf-8") as f:
                        f.write(job_content_text)
                    s3_text_url = upload_to_s3(text_path, bucket_name, f"job/{job_title}/sources/{extract_site_name(url)}/txt/{uuid.uuid4()}.txt")
                
                company_name = None
                post_title = None
                try:
                    company_link = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.name"))
                    )
                    company_name = parse_qs(urlparse(company_link.get_attribute("href")).query).get("company_nm", [None])[0]

                    post_title_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                    )
                    post_title = post_title_element.text
                except Exception:
                    pass

                if d_day:  # d_day 값이 존재하는 경우
                    deadline = calculate_deadline_from_dday(int(d_day))
                    due_type = '날짜'
                    due_date = deadline
                else:  # d_day 값이 없으면 '상시채용'
                    due_type = '상시채용'
                    due_date = None

                data = {
                    'site': extract_site_name(url),
                    'job_title': job_title,  # 동적으로 추출된 job_title
                    'due_type': due_type,
                    'due_date': due_date,
                    'company': company_name,
                    'notice_type': 'text',
                    'post_title': post_title,
                    'org_url': url,
                    's3_text_url': s3_text_url,
                    'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

                insert_into_db(data, connection)
                update_log_file(url, crawl_time)

    except Exception as e:
        print(f"Error processing {url}: {e}")

connection.close()
driver.quit()
