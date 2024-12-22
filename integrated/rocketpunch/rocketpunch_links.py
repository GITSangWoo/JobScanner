import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from zoneinfo import ZoneInfo
import re

# 변수 설정 : 검색 키워드
job_titles = {
    "DE": "데이터 엔지니어",
    "DA": "데이터 분석가",
    "FE": "프론트엔드 엔지니어",
    "BE": "백엔드 엔지니어",
    "MLE": "머신러닝 엔지니어"
}

# 변수 설정 : 로컬 저장 경로
LOCAL_PATH = './rocketpunch/'

kst = ZoneInfo("Asia/Seoul")

# Chrome driver 옵션 설정
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Headless 모드
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
    all_posts_links = []  # 데이터 엔지니어 공고 링크 리스트

    keyword = keyword.replace(" ", "+")
    base_url = f"https://www.rocketpunch.com/jobs?keywords={keyword}"  # "데이터" || "엔지니어"
    
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

def save_link_to_local(local_path, today_date, today_links):
    """ 로컬에 파일을 저장하는 함수
    :param local_path: 로컬 디렉터리 경로
    :param today_date: 오늘 날짜 (파일 이름)
    :param today_links: 저장할 링크 리스트
    :return: 파일 저장 성공 여부
    """
    try:
        if not os.path.exists(local_path):
            os.makedirs(local_path)  # 경로가 없으면 생성
        
        file_name = f"{today_date}.txt"
        file_path = os.path.join(local_path, file_name)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("\n".join(today_links))
        
        print(f"✅ 링크 파일 {file_name}이 로컬에 성공적으로 저장되었습니다")
        return True

    except Exception as e:
        print(f"⛔ [ERROR] 로컬로 파일을 저장하는데 에러 발생 {e}")
        return False

# 코드가 바로 실행되도록 변경된 부분
for job_abb, job_title in job_titles.items():
    # 로컬 링크 저장 경로 설정
    local_path = os.path.join(LOCAL_PATH, job_abb)
    today_links = get_all_links(job_title)

    today_date = datetime.now(tz=kst).strftime('%Y%m%d')
    # 오늘 수집한 링크를 로컬에 저장
    save_link_to_local(local_path, today_date, today_links)
# 로켓펀치 완료 
