# 패키지 불러오기
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, parse_qs, urlencode
from selenium.webdriver.common.keys import Keys
import boto3
import datetime
import time
import psutil
import shutil
import os

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
        print(f"Driver quit failed: {e}")

    # 프로세스 강제 종료
    for proc in psutil.process_iter(["pid", "name"]):
        if "chrome" in proc.info["name"].lower() or "chromedriver" in proc.info["name"].lower():
            try:
                proc.terminate()
                proc.wait(timeout=10)
                print(f"Process terminated: {proc.info}")
            except psutil.TimeoutExpired:
                print(f"Process termination timeout: {proc.info}")
                try:
                    proc.kill()  # 강제 종료
                    print(f"Process killed: {proc.info}")
                except Exception as kill_err:
                    print(f"Force kill failed: {kill_err}")
            except psutil.NoSuchProcess:
                print(f"Process already terminated: {proc.info}")
            except Exception as e:
                print(f"Process termination failed: {e}")

# AWS s3 설정
BUCKET_NAME = "t2jt"
S3_PATH_PREFIX_TEMPLATE = "job/{}/sources/saramin/links/"  # 키워드에 따른 동적 경로

# S3 클라이언트 생성
s3_client = boto3.client("s3")

# 키워드별 정보 설정
keywords_config = {
#    "데이터 엔지니어": {"job_title": "DE", "path_prefix": "DE"},
    "프론트엔드": {"job_title": "FE", "path_prefix": "FE"},
#    "백엔드": {"job_title": "BE", "path_prefix": "BE"},
#    "데이터 분석가": {"job_title": "DA", "path_prefix": "DA"}
#    "머신러닝 엔지니어": {"job_title": "MLE", "path_prefix": "MLE"},
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
        try:
            cleanup(driver)
        except Exception as e:
            print(f"cleanup 실패: {e}")
