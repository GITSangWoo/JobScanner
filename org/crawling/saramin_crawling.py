import boto3
from mysql.connector import pooling
import re
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qsl, urlencode, urljoin, unquote
from selenium.webdriver.chrome.options import Options
import requests
import uuid
import time
import logging
import psutil
import os

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
log_file = os.path.join(log_directory, f"{today}_saramin_post.log")

# 로그 설정
logging.basicConfig(
    filename=log_file,  # 로그 파일 경로
    filemode='a',       # 'w'는 매번 덮어씀, 'a'는 이어쓰기
    level=logging.INFO, # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # 로그 메시지 형식
)

# 컨테이너 작업 디렉토리 변경
os.chdir("/code/crawling")

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

if __name__ == "__main__":
    execute_for_all_keywords()


