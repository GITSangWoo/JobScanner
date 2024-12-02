from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import re
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

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
            logger.info(f"Checking page {page}: {page_url}")
            driver.get(page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#search-results > div.ui.job.items.segment.company-list > div.company.item'))
            )
            job_elements = driver.find_elements(By.CSS_SELECTOR, '#search-results > div.ui.job.items.segment.company-list > div.company.item')
            if not job_elements:
                logger.info(f"Page {page} has no job postings. Total pages: {page - 1}")
                return page - 1
            page += 1
    except TimeoutException:
        logger.warning(f"Timeout on page {page}")
        return page - 1
    except WebDriverException as e:
        logger.error(f"WebDriverException: {e}")
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
    """
    모든 페이지에서 채용공고 링크를 수집하는 함수
    나중에 직무(DA, DE, FE, BE...) 에 따라 공고 링크 수집
    """
    all_posts_links = [] # 데이터 엔지니어 공고 링크 리스트

    keyword = keyword.replace(" ", "+")
    base_url = f"https://www.rocketpunch.com/jobs?keywords={keyword}" # "데이터" || "엔지니어"
    
    try:
        total_pages = get_total_pages(base_url)
        if total_pages == 0:
            print(f"No job postings found for keyword: {keyword}")
            return []

        for page in range(1, total_pages + 1):
            print(f"{page}번째 페이지를 scraping 중입니다...")
            page_url = f"{base_url}&page={page}"
            page_links = get_links_from_page(page_url)
            all_posts_links.extend(page_links)

        return all_posts_links

    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return []

# rocketpunch_links.py 자체실행시 테스트용으로 __main__ 블록 추가
