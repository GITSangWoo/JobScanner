import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import boto3
import re
import time
import logging
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs, urlencode
from zoneinfo import ZoneInfo
from botocore.exceptions import NoCredentialsError, ClientError
from io import StringIO
import psutil
import shutil


# 로그 디렉토리 설정
log_directory = "/code/logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 오늘 날짜로 로그 파일 이름 설정
today = datetime.now().strftime("%Y%m%d")
log_file = os.path.join(log_directory, f"{today}_link.log")

# 로그 설정
logging.basicConfig(
    filename=log_file,  # 로그 파일 경로
    filemode='a',       # 'w'는 매번 덮어씀, 'a'는 이어쓰기
    level=logging.INFO, # 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # 로그 메시지 형식
)

os.chdir("/code/crwaling")  # 작업 디렉토리를 /code/crwaling로 변경
print(f"Current working directory: {os.getcwd()}")  # 현재 작업 디렉토리 확인

def incruit_link():
    try:
        logging.info("인크루트 링크 크롤링 시작")
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
        print(os.path.abspath("./incruit"))
        output_folder = f'{os.path.dirname(os.path.abspath(__file__))}/incruit'
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
                        response = requests.get(url, timeout=20)  # 10초 제한 설정
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
        
        logging.info("인크루트 링크 크롤링 완료")
    except Exception as e:
        logging.error(f"인크루트 링크 크롤링 중 오류 발생: {e}")


def jobkorea_link():
    try:
        logging.info("잡코리아 링크 크롤링 시작")

        # AWS S3 클라이언트 설정
        s3_client = boto3.client('s3')

        # ChromeOptions 설정
        options = webdriver.ChromeOptions()

        # Headless 옵션 추가
        options.add_argument("--headless")  # 화면을 표시하지 않음
        options.add_argument("--disable-gpu")  # GPU 비활성화 (Windows에서 필요할 수 있음)
        options.add_argument("--no-sandbox")  # 보안 옵션 비활성화 (Linux에서 필요할 수 있음)
        options.add_argument("--disable-dev-shm-usage")  # /dev/shm 공간 부족 해결
        options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
        options.add_argument("--disable-infobars")  # 자동화 브라우저 메시지 비활성화

        # User-Agent 설정
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")

        # WebDriver 초기화
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # 검색 키워드와 직무 약어 설정
        search_keywords = {
            "데이터 엔지니어": "DE",
            "프론트엔드": "FE",
            "백엔드": "BE",
            "데이터분석가": "DA",
            "머신러닝 엔지니어": "MLE"
        }

        # 오늘 날짜로 txt 파일 이름 설정
        today_date = datetime.now().strftime("%Y%m%d")

        # 이미 저장된 링크 불러오기 (S3에서만)
        def load_existing_links(bucket_name, s3_file_path):
            existing_links = set()

            # S3 파일에서 링크 읽기
            try:
                response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_path)
                content = response['Body'].read().decode('utf-8')
                existing_links.update(line.strip() for line in content.splitlines())
                print(f"S3에서 기존 링크를 로드했습니다. 총 {len(existing_links)}개의 링크.")
            except ClientError as e:
                if e.response['Error']['Code'] == "NoSuchKey":
                    print("S3에 오늘 파일이 존재하지 않습니다. 새로 생성합니다.")
                else:
                    print(f"S3 파일 로드 중 오류 발생: {e}")

            return existing_links

        # S3에 텍스트 데이터 업로드 함수
        def upload_to_s3_from_memory(data, bucket_name, s3_file_path):
            try:
                s3_client.put_object(Bucket=bucket_name, Key=s3_file_path, Body=data)
                print(f"파일이 S3에 성공적으로 업로드되었습니다. S3 경로: s3://{bucket_name}/{s3_file_path}")
            except NoCredentialsError:
                print("AWS 자격 증명 오류: 자격 증명이 없습니다.")
            except Exception as e:
                print(f"S3 업로드 중 오류 발생: {e}")

        # 특정 키워드에 대해 링크 크롤링
        def scrape_links_for_keyword(keyword, keyword_code, existing_links, bucket_name):
            base_url = f"https://www.jobkorea.co.kr/Search/?stext={keyword}&tabType=recruit&Page_No="
            new_links = []  # 새로 크롤링한 URL 저장
            page_number = 1  # 첫 페이지 번호

            while True:
                # 페이지 열기
                url = f"{base_url}{page_number}"
                driver.get(url)
                time.sleep(7)  # 페이지 로딩 대기

                # 검색 결과가 없으면 종료
                try:
                    no_results_message = driver.find_element(By.CLASS_NAME, "list-empty-result")
                    if "검색결과가 없습니다" in no_results_message.text:
                        print(f"{page_number}에 수집할 링크가 없으므로 링크 수집을 멈춥니다.")
                        break
                except Exception:
                    print(f"페이지 {page_number}: 검색 결과가 있습니다. 계속 진행합니다...")

                # article class="list" 내부의 링크 가져오기
                page_links = []  # 해당 페이지에서 새로 수집한 링크 저장
                try:
                    article_list = driver.find_element(By.CLASS_NAME, "list")  # article class="list" 선택
                    links = article_list.find_elements(By.TAG_NAME, "a")  # 해당 article 내부의 <a> 태그 찾기

                    for link in links:
                        href = link.get_attribute("href")
                        if href and href.startswith("https://www.jobkorea.co.kr/Recruit/GI_Read"):
                            # 'PageGbn=HH'가 포함된 링크는 제외
                            if "?PageGbn=HH" not in href:
                                # URL에서 "?"로 나눠서 앞부분만 가져오기
                                clean_href = href.split('?')[0]
                                if clean_href not in existing_links:
                                    page_links.append(clean_href)  # 직무 코드 없이 URL만 추가
                                    existing_links.add(clean_href)  # 중복 방지
                except Exception as e:
                    print(f"페이지 {page_number}에서 링크를 가져오는 데 오류가 발생했습니다: {e}")

                # 해당 페이지의 데이터를 저장
                if page_links:
                    new_links.extend(page_links)

                # 페이지 번호 증가
                page_number += 1

            # 새 링크를 직무 코드별 S3에 저장
            if new_links:
                s3_file_path = f"job/{keyword_code}/sources/jobkorea/links/{today_date}.txt"
                output_data = "\n".join(new_links)
                upload_to_s3_from_memory(output_data, bucket_name, s3_file_path)
                print(f"{keyword} ({keyword_code})에서 수집한 링크를 S3에 저장했습니다: {s3_file_path}")

            return new_links

        # 모든 키워드에 대해 크롤링
        def scrape_links():
            bucket_name = "t2jt"
            all_new_links = []

            for keyword, keyword_code in search_keywords.items():
                # 기존 링크 로드 (각 직무 코드별로 별도 파일)
                s3_file_path = f"job/{keyword_code}/sources/jobkorea/links/{today_date}.txt"
                existing_links = load_existing_links(bucket_name, s3_file_path)
                
                print(f"검색 키워드: {keyword} ({keyword_code})")
                new_links = scrape_links_for_keyword(keyword, keyword_code, existing_links, bucket_name)
                all_new_links.extend(new_links)
                print(f"{keyword}에서 {len(new_links)}개의 새로운 링크를 발견하였습니다.")

            # 총 결과 출력
            print(f"총 {len(all_new_links)}개의 새로운 링크를 발견하였습니다.")

        # 크롤링 실행
        scrape_links()

        # 브라우저 종료
        driver.quit()

        logging.info("잡코리아 링크 크롤링 완료")
    except Exception as e:
        logging.error(f"잡코리아 링크 크롤링 중 오류 발생: {e}")


def jumpit_link():
    try:
        logging.info("점핏 링크 크롤링 시작")
        # 검색 URL 리스트 설정
        job_url_list = {
            "DE": [
                "https://jumpit.saramin.co.kr/search?sort=relation&keyword=데이터%20엔지니어"
            ],
            "FE": [
                "https://jumpit.saramin.co.kr/search?sort=relation&keyword=프론트%20엔지니어"
            ],
            "BE": [
                "https://jumpit.saramin.co.kr/search?sort=relation&keyword=백엔드%20엔지니어"
            ],
            "DA": [
                "https://jumpit.saramin.co.kr/search?sort=relation&keyword=데이터%20분석가"
            ],
            "MLE": [
                "https://jumpit.saramin.co.kr/search?sort=relation&keyword=머신러닝%20엔지니어"
            ]
        }

        # 셀레니움 웹 드라이버 설정
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 화면을 표시하지 않음
        options.add_argument("--disable-gpu")  # GPU 비활성화 (Windows에서 필요할 수 있음)
        options.add_argument("--no-sandbox")  # 보안 옵션 비활성화 (Linux에서 필요할 수 있음)
        options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 사용 비활성화
        options.add_argument("--disable-background-timer-throttling")  # 백그라운드 타이머 제한 비활성화
        options.add_argument("--disable-renderer-backgrounding")  # 렌더링 백그라운드 비활성화
        options.add_argument("--disable-extensions")  # 확장 프로그램 비활성화
        options.add_argument("--disable-infobars")  # 정보 바 비활성화
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
        options.add_argument(f"user-agent={user_agent}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # 오늘 날짜로 로그 파일 이름 설정
        today = datetime.today().strftime('%Y%m%d')

        # 로그 파일을 찾을 디렉토리 설정
        log_directory = f'{os.path.dirname( os.path.abspath(__file__) )}/jumpit'  # 현재 디렉토리
        today_log_file_name = os.path.join(log_directory,f"{today}.log")

        # 디렉토리가 존재하는지 확인하고, 없으면 생성
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
            print(f"{log_directory} 디렉토리가 없어서 새로 생성되었습니다.")
        else:
            print(f"{log_directory} 디렉토리가 이미 존재합니다.")

        log_files = [os.path.join(log_directory, f) for f in os.listdir(log_directory) if re.match(r'^\d{8}\.log$', f)]

        # 가장 최근에 생성된 로그 파일 찾기
        recent_log_file_name = None  # 기본값을 None으로 설정
        if log_files:
            log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            recent_log_file_name = log_files[0]  # 가장 최근의 로그 파일을 선택
            print(f"Found the most recent log file: {recent_log_file_name}")
        else:
            print("No log files found in the directory. All URLs will be marked as 'update'.")

        try:
            # 이전 로그 파일이 없으면 빈 딕셔너리로 설정 (오늘 크롤링한 URL과 비교할 기준이 없으므로)
            previous_urls = {}

            # 오늘 크롤링한 URL과 비교하여 상태 설정
            for job_key, urls in job_url_list.items():
                for url in urls:
                    # 페이지 열기
                    driver.get(url)

                    # 페이지 로딩 대기: 페이지가 완전히 로드될 때까지 기다리기
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.TAG_NAME, "a"))
                    )

                    # 스크롤 내리기 및 링크 추출 반복
                    previous_height = driver.execute_script("return document.body.scrollHeight")  # 현재 페이지의 높이를 가져옴

                    # 페이지가 끝까지 스크롤될 때까지 반복
                    while True:
                        # 페이지에서 모든 <a> 태그를 찾음
                        links = driver.find_elements(By.TAG_NAME, "a")

                        # 링크를 모두 추가 (중복 확인은 데이터베이스에서 처리)
                        for link in links:
                            retry_count = 3  # 최대 재시도 횟수
                            for attempt in range(retry_count):
                                try:
                                    href = link.get_attribute("href")
                                    # 정규 표현식으로 'position/숫자' 형식의 링크만 필터링
                                    if href and re.search(r'position/\d+$', href):
                                        # D-day 정보 추출
                                        d_day = None  # 기본값을 None으로 설정
                                        try:
                                            # D-day 정보를 담고 있는 요소를 찾기
                                            d_day_elements = link.find_elements(By.XPATH, ".//div[contains(@class, 'sc-d609d44f-3')]/span")
                                            if d_day_elements:
                                                d_day_text = d_day_elements[0].text.strip()
                                                print(f"D-day Text: {d_day_text}")  # D-day 추출된 값 확인
                                                if "상시" in d_day_text:
                                                    d_day = None  # 상시는 null로 저장
                                                elif d_day_text.startswith("D-"):
                                                    d_day = int(d_day_text[2:])  # D-숫자에서 숫자만 추출
                                                else:
                                                    d_day = None
                                        except Exception as e:
                                            print(f"D-day 추출 실패: {e}")

                                        # 로그에 바로 기록
                                        job = job_key
                                        notice_status = "update"
                                        work_status = "null"
                                        done_time = "null"
                                        print(f"링크: {href}, D-day: {d_day}")  # D-day 값도 함께 출력
                                        with open(today_log_file_name, 'a', encoding='utf-8') as file:
                                            file.write(f"{job},{href},{notice_status},{work_status},{done_time},{d_day if d_day is not None else 'null'}\n")
                                    break  # 성공하면 루프 종료

                                except StaleElementReferenceException:
                                    print(f"StaleElementReferenceException 발생. 재시도 중... ({attempt + 1}/{retry_count})")
                                    time.sleep(1)  # 재시도 전에 잠시 대기
                                    if attempt == retry_count - 1:
                                        print(f"재시도 실패: {link}. 해당 링크를 건너뜁니다.")
                                        continue

                        # 스크롤을 페이지 끝까지 내리기
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                        # 잠시 대기하여 새로운 요소들이 로드될 시간을 줌
                        time.sleep(2)  # 2초간 대기, 이 시간은 페이지 로딩 속도에 맞게 조절

                        # 새로운 페이지 높이가 이전과 같다면 스크롤을 더 이상 내릴 필요가 없으므로 종료
                        new_height = driver.execute_script("return document.body.scrollHeight")
                        if new_height == previous_height:
                            break  # 더 이상 새로운 요소가 로드되지 않으면 반복 종료

                        previous_height = new_height  # 이전 높이를 업데이트

                    print(f"{job_key} 직무 크롤링 완료")

        except Exception as e:
            print(f"Error in jumpit_link: {e}")

        finally:
            print("크롤링이 완료되었으며 로그 파일에 실시간으로 저장되었습니다.")
            driver.quit()

        logging.info("점핏 링크 크롤링 완료")
    except Exception as e:
        logging.error(f"점핏 링크 크롤링 중 오류 발생: {e}")


def rocketpunch_link():
    try:
        logging.info("로켓펀치 링크 크롤링 시작")

        # 변수 설정 : 검색 키워드
        job_titles = {
            "DE":"데이터 엔지니어", 
            "DA":"데이터 분석가", 
            "FE":"프론트엔드 엔지니어", 
            "BE":"백엔드 엔지니어", 
            "MLE":"머신러닝 엔지니어"
            }

        # 변수 설정 : 링크 저장을 위한 S3
        BUCKET_NAME = 't2jt'
        S3_LINK_PATH = 'job/{abb}/sources/rocketpunch/links/'

        # Chrome driver 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Headless 모드
        chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
        chrome_options.add_argument("--no-sandbox")  # 리소스 제약 없는 환경에서 실행

        def get_total_pages(base_url):
            """ Rocketpunch의 유효한 페이지 수를 반환하는 함수."""
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            try:
                page = 1
                while True:
                    page_url = f"{base_url}&page={page}"
                    driver.get(page_url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#search-results > div.ui.job.items.segment.company-list > div.company.item'))
                    )
                    job_elements = driver.find_elements(By.CSS_SELECTOR, '#search-results > div.ui.job.items.segment.company-list > div.company.item')
                    if not job_elements:
                        print(f"Page {page} has no job postings. Total pages: {page - 1}")
                        return page - 1
                    page += 1
            except TimeoutException:
                print(f"Timeout on page {page}")
                return page - 1
            except WebDriverException as e:
                print(f"WebDriverException: {e}")
                return page - 1
            finally:
                driver.quit()

        def get_links_from_page(page_url):
            """ 
            한 페이지에서 채용공고 링크를 크롤링하는 함수
            :param page_url: 특정 페이지 URL
            :return: 페이지 내 공고 링크 리스트
            """
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            try:
                driver.get(page_url)

                # 모든 공고가 로드될 때까지 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#search-results > div.ui.job.items.segment.company-list > div.company.item'))
                )

                links = driver.find_elements(By.TAG_NAME, "a")
                pattern = re.compile(r"^https://www\.rocketpunch\.com/jobs/\d+/[\w\-\%]+")
                page_links = [link.get_attribute("href") for link in links if link.get_attribute("href") and pattern.search(link.get_attribute("href"))]
                return page_links
            
            except TimeoutException:
                print(f"Timeout while loading page: {page_url}")
                return []
            except WebDriverException as e:
                print(f"WebDriver error while accessing page: {e}")
                return []
            finally:
                driver.quit()

        def get_all_links(keyword):
            """ 모든 페이지에서 채용공고 링크를 수집하는 함수, 나중에 직무(DA, DE, FE, BE...) 에 따라 공고 링크 수집"""
            all_posts_links = [] # 데이터 엔지니어 공고 링크 리스트

            keyword = keyword.replace(" ", "+")
            base_url = f"https://www.rocketpunch.com/jobs?keywords={keyword}" # "데이터" || "엔지니어"
            
            try:
                total_pages = get_total_pages(base_url)
                if total_pages == 0:
                    print(f"키워드 {keyword}에 해당하는 채용공고가 없습니다!")
                    return []

                for page in range(1, total_pages + 1):
                    page_url = f"{base_url}&page={page}"
                    page_links = get_links_from_page(page_url)
                    all_posts_links.extend(page_links)

                return all_posts_links

            except Exception as e:
                print(f"Unexpected error occurred: {e}")
                return []
            
        def save_link_to_s3(bucket_name, s3_link_path, today_date, today_links):
            """ S3 버킷에 파일을 업로드합니다.
            :param file_name: 업로드할 파일
            :param bucket: 업로드될 버킷
            :param object_name: S3 객체이름. 없으면 file_name 사용
            :return: 파일이 업로드되면 True, 아니면 False
            """
            # S3 클라이언트 생성, 특정 클라이언트(다른 계정)을 경우에는 세션을 먼저 설정
            s3 = boto3.client('s3')
            file_content = "\n".join(today_links)
            list_key = f"{s3_link_path}{today_date}.txt"
            # S3에 파일 업로드
            try:
                s3.put_object(Bucket=bucket_name, Key=list_key, Body=file_content)
                print(f"✅ 링크 파일 {list_key}이 성공적으로 S3에 업데이트 되었습니다")
                return True
            except Exception as e:
                print(f"⛔ [ERROR] S3로 파일을 업로드하는데 에러 발생 {e}")
                return False

        
        for job_abb, job_title in job_titles.items():
            # s3 링크 저장 경로 설정
            s3_link_path = S3_LINK_PATH.format(abb = job_abb)
            today_links = get_all_links(job_title)

            today_date = datetime.now().strftime('%Y%m%d')
            # 일단 오늘 수집한거 파일없이 메모리에서 바로 s3에 저장
            save_link_to_s3(BUCKET_NAME, s3_link_path, today_date, today_links)
        logging.info("로켓펀치 링크 크롤링 완료")
    except Exception as e:
        logging.error(f"로켓펀치 링크 크롤링 중 오류 발생: {e}")

def saramin_link():
    try:
        logging.info("사람인 링크 크롤링 시작")
        # URL에서 rec_idx 값까지만 포함된 URL 반환 함수
        def extract_rec_idx_url(url):
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            rec_idx = query_params.get("rec_idx", [None])[0]
            if rec_idx:
                new_query = urlencode({"rec_idx": rec_idx})
                return f"{base_url}?{new_query}"
            return base_url

        def cleanup(driver):
            try:
                driver.quit()
            except Exception as e:
                logging.warning(f"Driver quit failed: {e}")

            # 프로세스 강제 종료
            for proc in psutil.process_iter(["pid", "name"]):
                if "chrome" in proc.info["name"].lower() or "chromedriver" in proc.info["name"].lower():
                    try:
                        proc.kill()  # 강제 종료
                        print(f"Process killed: {proc.info}")
                    except psutil.NoSuchProcess:
                        continue
                    except Exception as e:
                        print(f"Failed to kill process: {e}")

        # AWS s3 설정
        BUCKET_NAME = "t2jt"
        S3_PATH_PREFIX_TEMPLATE = "job/{}/sources/saramin/links/"  # 키워드에 따른 동적 경로

        # S3 클라이언트 생성
        s3_client = boto3.client("s3")

        # 키워드별 정보 설정
        keywords_config = {
            "데이터 엔지니어": {"job_title": "DE", "path_prefix": "DE"},
            "프론트엔드": {"job_title": "FE", "path_prefix": "FE"},
            "백엔드": {"job_title": "BE", "path_prefix": "BE"},
            "데이터 분석가": {"job_title": "DA", "path_prefix": "DA"},
            "머신러닝 엔지니어": {"job_title": "MLE", "path_prefix": "MLE"}
        }

        # WebDriver 설정
        for keyword, config in keywords_config.items():
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--incognito")
            #chrome_options.add_argument(f"--user-data-dir={temp_dir}")  # 사용자 데이터 디렉토리 강제 지정
            chrome_options.add_argument("--disable-cache")
            chrome_options.add_argument("--disable-application-cache")  # 애플리케이션 캐시 비활성화
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-gpu")  # GPU 캐시 비활성화 (필요한 경우)
            chrome_options.add_argument("--no-sandbox")  # 샌드박스 비활성화 (권장)
            chrome_options.add_argument("--disable-dev-shm-usage")  # 공유 메모리 비활성화 (리소스 관리)
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")  # User-Agent 설정

            try:
                print(f"키워드 '{keyword}' 작업 시작")

                # 각 키워드별로 새로운 브라우저 인스턴스 실행. 브라우저 실행 후 캐시 비활성화
                driver = webdriver.Chrome(options=chrome_options)
                driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
                time.sleep(2)
                # 명시적으로 캐시 및 스토리지 데이터 삭제
                driver.execute_cdp_cmd(
                    "Storage.clearDataForOrigin",
                    {
                        "origin": "https://www.saramin.co.kr",
                        "storageTypes": "all"
                    }
                )


                # Ctrl + F5 강력 새로고침
                try:
                    body = driver.find_element(By.TAG_NAME, "body")
                    body.send_keys(Keys.CONTROL, Keys.F5)  # Ctrl + F5 입력
                    print("브라우저 강력 새로고침 (Ctrl + F5) 완료")
                except Exception as e:
                    print(f"Ctrl + F5 새로고침 실패, 강제로 URL 재로드: {e}")
                    driver.refresh()
                time.sleep(3)

                # URL에 nocache 파라미터 추가
                url = f"https://www.saramin.co.kr/zf_user/?nocache={int(time.time())}"
                driver.get(url)
                print(f"캐시 무효화된 URL로 접근: {url}")
                time.sleep(5)

                # 수집 시점
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                today_date = datetime.now().strftime("%Y%m%d")

                # S3 파일 경로
                s3_path_prefix = S3_PATH_PREFIX_TEMPLATE.format(config["path_prefix"])
                s3_file_path = f"{s3_path_prefix}{today_date}.txt"

                # 검색어 입력 및 실행
                search_box = driver.find_element(By.CLASS_NAME, "search")
                search_box.click()
                time.sleep(2)
                search_input = driver.find_element(By.XPATH, '//input[@id="ipt_keyword_recruit"]')
                search_input.click()
                time.sleep(2)
                search_input.clear()
                search_input.send_keys(keyword)
                time.sleep(2)
                search_button = driver.find_element(By.XPATH, '//button[@id="btn_search_recruit"]')
                search_button.click()
                print(f"'{keyword}' 검색 완료!")
                time.sleep(7)

                # 모든 페이지 데이터 수집
                page = 1
                job_data_list = []
                while True:
                    print(f"현재 페이지: {page}")
                    try:
                        job_elements = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located(
                                (By.XPATH, '//div[@id="recruit_info_list"]//div[contains(@class, "item_recruit")]')
                            )
                        )
                        for job_element in job_elements:
                            try:
                                title_element = job_element.find_element(By.XPATH, './/h2[@class="job_tit"]/a')
                                title = title_element.get_attribute("title")
                                url = title_element.get_attribute("href")
                                org_url = extract_rec_idx_url(url)
                                company_element = job_element.find_element(By.XPATH, './/div[@class="area_corp"]//a')
                                company_name = company_element.text if company_element else "Unknown"
                                job_data_list.append({
                                    "URL_CR_TIME": current_time,
                                    "SITE": "saramin",
                                    "JOB_TITLE": config["job_title"],
                                    "COMPANY": company_name,
                                    "POST_TITLE": title,
                                    "ORG_URL": org_url
                                })
                            except Exception as e:
                                print(f"요소 처리 중 오류 발생: {e}")
                        time.sleep(5)

                        # 다음 페이지로 이동
                        next_page = driver.find_element(By.XPATH, f'//a[@page="{page + 1}"]')
                        next_page.click()
                        time.sleep(5)
                        page += 1
                    except Exception:
                        print(f"'{keyword}' 작업: 마지막 페이지 도달")
                        break

                # S3 업로드 준비
                s3_content = "\n".join(
                    f"URL_CR_TIME: {job['URL_CR_TIME']}, SITE: {job['SITE']}, JOB_TITLE: {job['JOB_TITLE']}, "
                    f"COMPANY: {job['COMPANY']}, POST_TITLE: {job['POST_TITLE']}, ORG_URL: {job['ORG_URL']}"
                    for job in job_data_list
                )

                # S3에 데이터 업로드
                s3_client.put_object(
                    Bucket=BUCKET_NAME,
                    Key=s3_file_path,
                    Body=s3_content.encode("utf-8-sig"),
                    ContentType="text/plain"
                )
                print(f"S3에 파일 업로드 완료: s3://{BUCKET_NAME}/{s3_file_path}")

            except Exception as e:
                print(f"오류 발생: {e}")

            finally:
                cleanup(driver)
        logging.info("사람인 링크 크롤링 완료")
    except Exception as e:
        logging.error(f"사람인 링크 크롤링 중 오류 발생: {e}")


def wanted_link():
    try:
        logging.info("원티드 링크 크롤링 시작")
        if not os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/wanted"):
            os.makedirs(f"{os.path.dirname(os.path.abspath(__file__))}/wanted")  # 디렉토리 생성  
        
        def log_error(error_message):
            """오류를 makelog_err.log 파일에 기록"""
            # ./wanted 디렉토리가 없으면 생성
            with open('./wanted/makelog_err.log', 'a', encoding='utf-8') as err_file:
                timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                err_file.write(f"{timestamp},{error_message}\n")

        job_url_list = {
            "DE": [
                "https://www.wanted.co.kr/search?query=데이터+엔지니어&tab=position",
            ],
            "FE": [
                "https://www.wanted.co.kr/search?query=프론트엔드&tab=position"
            ],
            "BE": [
                "https://www.wanted.co.kr/search?query=백엔드&tab=position"
            ],
            "DA": [
                "https://www.wanted.co.kr/search?query=데이터+분석가&tab=position",
            ],
            "MLE": [
                "https://www.wanted.co.kr/search?query=머신러닝+엔지니어&tab=position",
            ]
        }

        try:
            # 셀레니움 웹 드라이버 설정
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--window-size=1920x1080")
            options.add_argument("--disable-background-networking")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"
            options.add_argument(f"user-agent={user_agent}")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            # 오늘 날짜로 로그 파일 이름 설정
            today = datetime.now().strftime('%Y%m%d')
            today_log_file_name = f"{os.path.dirname(os.path.abspath(__file__))}/wanted/{today}.log"

            # 로그 파일을 찾을 디렉토리 설정
            log_directory = f"{os.path.dirname(os.path.abspath(__file__))}/wanted"  # 원하는 디렉토리로 변경
            log_files = [f for f in os.listdir(log_directory) if re.match(r'^\d{8}\.log$', f)]

            # 가장 최근에 생성된 로그 파일 찾기
            if log_files:
                # 파일들을 생성 시간 기준으로 정렬하고 가장 최근 파일을 선택
                log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_directory, x)), reverse=True)
                recent_log_file_name = log_files[0]  # 가장 최근의 로그 파일을 선택
                print(f"Found the most recent log file: {recent_log_file_name}")
            else:
                print("No log files found in the directory. All URLs will be marked as 'update'.")
                recent_log_file_name = None  # recent_log_file_name을 None으로 설정

            # 이전 로그 파일이 존재하는지 확인하고 읽기
            previous_urls = {}  # 이전 로그에 있는 URL 및 해당 job
            #if os.path.exists(os.path.join(log_directory, recent_log_file_name)):
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
                                if notice_status != "deleted":  # "deleted" 상태인 URL은 제외
                                    previous_urls[url] = job  # URL에 해당하는 job을 저장
    
            # 오늘 크롤링한 URL을 수집
            all_links = []  # 오늘 수집한 모든 링크
            job_for_links = {}  # 각 링크에 해당하는 job을 기록하기 위한 dictionary

            # 각 job (키값)에 대한 URL 처리
            for job_key, urls in job_url_list.items():
                for url in urls:
                    # 페이지 열기
                    driver.get(url)

                    # 페이지 로딩 대기: 페이지가 완전히 로드될 때까지 기다기
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "a"))
                    )

                    # 정규 표현식 패턴 (wd/ 뒤에 숫자가 있는 URL을 찾는 패턴)
                    pattern = re.compile(r'wd/\d+$')

                    # 스크롤 내리기 및 링크 추출 반복
                    previous_height = driver.execute_script("return document.body.scrollHeight")  # 현재 페이지의 높이를 가져옴

                    while True:
                        # 페이지에서 모든 <a> 태그를 찾음
                        links = driver.find_elements(By.TAG_NAME, "a")

                        # 이미 가져온 링크들을 확인하고 중복되지 않게 추가
                        for link in links:
                            href = link.get_attribute("href")
                            # 정규 표현식으로 'wd/숫자' 형식의 링크만 필터링
                            if href and pattern.search(href) and href not in all_links:
                                all_links.append(href)
                                job_for_links[href] = job_key  # 링크에 해당하는 job 기록

                        # 스크롤을 페이지 끝까지 내리기
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                        # 잠시 대기하여 새로운 요소들이 로드될 시간을 줌
                        time.sleep(2)  # 2초간 대기, 이 시간은 페이지 로딩 속도에 맞게 조절

                        # 새로운 페이지 높이가 이전과 같다면 스크롤을 더 이상 내릴 필요가 없으므로 종료
                        new_height = driver.execute_script("return document.body.scrollHeight")
                        if new_height == previous_height:
                            break  # 더 이상 새로운 요소가 로드되지 않으면 반복 종료

                        previous_height = new_height  # 이전 높이를 업데이트

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
                work_status = "done"  # 상태는 'done'으로 설정
                done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                job = job_for_links.get(url, 'unknown')  # 해당 URL의 job을 가져옴
                log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")

            # 2. 새로 추가된 링크 처리 (오늘만 있는 링크)
            new_urls = all_urls_set - previous_urls_set  # 오늘만 존재하는 링크
            for url in new_urls:
                notice_status = "update"
                work_status = "null"
                done_time = "null"
                job = job_for_links[url]  # 새 URL에는 해당 job_key 값을 사용
                log_data_other.append(f"{job},{url},{notice_status},{work_status},{done_time}")

            # 3. 삭제된 링크 처리 (어제 있었으나 오늘은 없는 링크)
            deleted_urls = previous_urls_set - all_urls_set  # 어제는 있었지만 오늘은 없는 것
            for url in deleted_urls:
                notice_status = "deleted"
                work_status = "done"
                done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 삭제된 시간을 현재 시간으로 설정
                # 이전 로그에서 해당 URL의 job을 가져옴
                job = previous_urls.get(url, 'unknown')  # 어제의 job 값을 사용
                log_data_deleted.append(f"{job},{url},{notice_status},{work_status},{done_time}")

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

            # 브라우저 종료
            driver.quit()

        except Exception as e:
            # 오류 발생 시 오류 메시지 기록
            error_message = str(e)
            log_error(error_message)
            # 프로그램 종료 전 브라우저 종료
            if 'driver' in locals():
                driver.quit()
        logging.info("원티드 링크 크롤링 완료")
    except Exception as e:
        logging.error(f"원티드 링크 크롤링 중 오류 발생: {e}")


# 크롤링 작업 완료 후 모든 WebDriver 프로세스를 강제 종료:
def clean_up_chrome_processes():
    os.system("pkill -f chromedriver || true")
    os.system("pkill -f chrome || true")

clean_up_chrome_processes()


def link_main():
    logging.info(f"인크루트 링크 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    incruit_link()
    logging.info(f"인크루트 링크 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(5)

    logging.info(f"잡코리아 링크 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    jobkorea_link()
    logging.info(f"잡코리아 링크 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(5)

    logging.info(f"점핏 링크 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    jumpit_link()
    logging.info(f"점핏 링크 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(5)

    logging.info(f"로켓펀치 링크 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rocketpunch_link()
    logging.info(f"로켓펀치 링크 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(5)

    logging.info(f"사람인 링크 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    saramin_link()
    logging.info(f"사람인 링크 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(5)

    logging.info(f"원티드 링크 크롤링 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    wanted_link()
    logging.info(f"원티드 링크 크롤링 종료: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    clean_up_chrome_processes()

if __name__ == "__main__":
    link_main()