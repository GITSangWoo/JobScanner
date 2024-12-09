from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs, urlencode
import boto3
import datetime
import time
import os


# URL에서 rec_idx 값까지만 포함된 URL 반환 함수
def extract_rec_idx_url(url):
    """
    URL에서 rec_idx 값까지만 포함된 URL을 반환
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    
    # rec_idx 값만 포함한 쿼리 스트링 생성
    rec_idx = query_params.get("rec_idx", [None])[0]
    if rec_idx:
        new_query = urlencode({"rec_idx": rec_idx})
        return f"{base_url}?{new_query}"
    return base_url

# AWS s3 설정
BUCKET_NAME = "t2jt"               # S3 버킷 이름
S3_PATH_PREFIX = "job/DE/sources/saramin/links/"  # S3 경로

# S3 클라이언트 생성 (자격 증명은 ~/.aws/credentials에서 읽음)
s3_client = boto3.client("s3")

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-cache")  # 캐시 비활성화
chrome_options.add_argument("--incognito")   # 시크릿 모드로 실행
#chrome_options.add_argument("--disk-cache-dir=/dev/null")  # 디스크 캐시를 비활성화
#chrome_options.add_argument("--disable-application-cache")  # 애플리케이션 캐시 비활성화
#chrome_options.add_argument("--disable-gpu")  # GPU 가속 비활성화 (필요한 경우)
#chrome_options.add_argument("--no-sandbox")  # 샌드박스 비활성화

# Selenium WebDriver 설정
driver = webdriver.Chrome(options=chrome_options)

# DevTools Protocol을 사용하여 캐시 비활성화
driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})

# 사람인 홈페이지 접속
url = "https://www.saramin.co.kr/zf_user/"
driver.get(url)
time.sleep(7)

driver.delete_all_cookies()
driver.execute_script("window.localStorage.clear();")
driver.execute_script("window.sessionStorage.clear();")

try:
    # 수집 시점
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_date = datetime.datetime.now().strftime("%Y%m%d")  # 오늘 날짜 (YYYYMMDD)

    # s3 파일 경로
    s3_file_path = f"{S3_PATH_PREFIX}{today_date}.txt"

    # 검색창 선택 및 검색어 입력
    #search_box = WebDriverWait(driver, 5).until(
    #    EC.presence_of_element_located((By.CLASS_NAME, "search"))
    #)
    search_box = driver.find_element(By.CLASS_NAME, "search")
    search_box.click()
    time.sleep(5)

    search_input = driver.find_element(By.XPATH, '//input[@id="ipt_keyword_recruit"]')
    search_input.click()
    time.sleep(5)
    
    keyword = "데이터 엔지니어"
    search_input.send_keys(keyword)  # 검색어 입력
    time.sleep(3) #추가
    #search_input.send_keys(Keys.RETURN)  # 검색 실행
    search_button = driver.find_element(By.XPATH, '//button[@id="btn_search_recruit"]')  # 정확한 XPATH 사용
    search_button.click()  # 검색 버튼 클릭
    print("검색 완료!")

    # 검색 결과 로드 대기
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "recruit_info_list"))
    )

    # 모든 페이지 데이터 수집
    page = 1  # 현재 페이지 번호
    job_data_list = [] # 데이터를 저장할 리스트

    while True:
        print(f"현재 페이지: {page}")

        # 현재 페이지 데이터 수집
        job_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@id="recruit_info_list"]//div[contains(@class, "item_recruit")]')
            )
        )

        for job_element in job_elements:
            try:
                # 제목과 URL
                title_element = job_element.find_element(By.XPATH, './/h2[@class="job_tit"]/a')
                title = title_element.get_attribute("title")
                url = title_element.get_attribute("href")

                # URL에서 rec_idx 값까지만 포함된 URL 생성
                org_url = extract_rec_idx_url(url)  # URL 가공

                # 기업명
                company_element = job_element.find_element(By.XPATH, './/div[@class="area_corp"]//a')
                company_name = company_element.text if company_element else "Unknown"

                # 데이터 리스트에 추가
                job_data_list.append({
                    "URL_CR_TIME": current_time,
                    "SITE": "saramin",
                    "JOB_TITLE": keyword,
                    "COMPANY": company_name,
                    "POST_TITLE": title,
                    "ORG_URL": org_url  # 가공된 URL 저장
                })
            except Exception as e:
                print(f"요소 처리 중 오류 발생: {e}")
        time.sleep(7)

        # 다음 페이지로 이동
        try:
            next_page = driver.find_element(By.XPATH, f'//a[@page="{page + 1}"]')
            next_page.click()  # 다음 페이지로 이동
            time.sleep(7)
            page += 1
        except Exception as e:
            print("마지막 페이지에 도달했거나 다음 페이지로 이동할 수 없습니다.")
            break

    # S3로 데이터 업로드
    s3_content = ""
    for job in job_data_list:
        formatted_line = (
            f"URL_CR_TIME: {job['URL_CR_TIME']}, "
            f"SITE: {job['SITE']}, "
            f"JOB_TITLE: {job['JOB_TITLE']}, "
            f"COMPANY: {job['COMPANY']}, "
            f"POST_TITLE: {job['POST_TITLE']}, "
            f"ORG_URL: {job['ORG_URL']}\n"
        )
        s3_content += formatted_line

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
    # 자동 종료 안되게
    #input("Press Enter to close the browser...")
    driver.quit()