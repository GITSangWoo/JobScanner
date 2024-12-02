import re
import os
import time
from datetime import datetime, timedelta
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 검색 키워드 설정
search_keyword = "데이터 엔지니어"

# Selenium 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Jumpit 페이지 열기
driver.get("https://jumpit.saramin.co.kr/")

# 페이지 로딩 대기
time.sleep(5)

# 팝업 닫기
try:
    close_popup = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.sc-c82c57bb-4.cLpfjF"))
    )
    close_popup.click()
    print("팝업 닫음.")
except Exception as e:
    print(f"팝업 닫기 실패: {e}")

# 검색창 찾기 및 검색
try:
    search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='검색어를 입력해주세요']")
    search_input.send_keys(search_keyword)  # 검색어 입력
    search_input.send_keys(Keys.RETURN)  # Enter 키 입력
    print(f"'{search_keyword}' 검색어 입력 완료.")
except Exception as e:
    print(f"검색창을 찾을 수 없습니다: {e}")
    driver.quit()
    exit()

# 검색 결과 로딩 대기
time.sleep(5)

# 링크와 D-day 값을 저장할 딕셔너리
link_data = {}

# 정규 표현식 패턴 (position/ 뒤에 숫자가 있는 URL을 찾는 패턴)
pattern = re.compile(r'position/\d+$')

# 스크롤 내리기 및 링크 추출 반복
previous_height = driver.execute_script("return document.body.scrollHeight")

while True:
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        if href and pattern.search(href) and href not in link_data:
            # D-day 정보 추출
            try:
                d_day_elements = link.find_elements(By.XPATH, ".//div[contains(@class, 'sc-d609d44f-3')]/span")
                if d_day_elements:
                    d_day_text = d_day_elements[0].text.strip()
                    if "상시" in d_day_text:
                        d_day = None  # 상시는 null로 저장
                    elif d_day_text.startswith("D-"):
                        d_day = int(d_day_text[2:])  # D-숫자에서 숫자만 추출
                    else:
                        d_day = None
                else:
                    d_day = None
            except Exception as e:
                print(f"D-day 추출 실패: {e}")
                d_day = None

            link_data[href] = d_day
            print(f"링크: {href}, D-day: {d_day}")

    # 스크롤 내리기
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    # 새로운 높이 확인
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == previous_height:
        break
    previous_height = new_height

# 디렉터리 생성 (로컬 저장용 디렉터리)
output_folder = "links"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 오늘 날짜 기반 파일 이름 생성
today = datetime.now().strftime("%Y%m%d")
output_file_path = os.path.join(output_folder, f"{today}.log")
log_file_name=os.path.join(output_folder, f"{today}.log")

yesterday= (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
yesterday_log_file=os.path.join(output_folder, f"{yesterday}.log")

# 어제 로그 파일이 있으면 읽기
previous_urls = {}
if os.path.exists(yesterday_log_file):
    with open(yesterday_log_file, 'r', encoding='utf-8') as file:
        for line in file.readlines()[1:]:  # 첫 번째 줄은 header
            columns = line.strip().split(',')
            url = columns[0]
            notice_status = columns[1]
            work_status = columns[2]
            done_time = columns[3]
            previous_urls[url] = {
                'notice_status': notice_status,
                'work_status': work_status,
                'done_time': done_time
            }

# 오늘 로그 파일에 기록할 내용 생성
log_data = []

# 오늘 크롤링한 URL과 어제 로그 파일을 비교하여 상태 설정
for url in link_data:
    if os.path.exists(yesterday_log_file):
        if url in previous_urls:
            # 어제 로그 파일에 URL이 있고, work_status가 "done"이 아니면 그대로 가져옴
            if previous_urls[url]['work_status'] != "done":
                # 작업이 필요하거나 아직 완료되지 않은 경우
                notice_status = previous_urls[url]['notice_status']
                work_status = previous_urls[url]['work_status']
                done_time = previous_urls[url]['done_time']
            else:
                # "done" 상태면 "exist"로 설정하고, done_time을 그대로 사용
                notice_status = "exist"
                work_status = "done"
                done_time = previous_urls[url]['done_time']
        else:
            # 어제 로그 파일에 없으면 상태를 "deleted"로 설정
            notice_status = "deleted"
            work_status = "done"
            done_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')  # 삭제된 시간을 현재 시간으로
    else:
        # 어제 로그 파일이 없으면 모든 URL은 "update"로 설정
        notice_status = "update"
        work_status = "null"
        done_time = "null"

    log_data.append(f"{url},{notice_status},{work_status},{done_time}")

# 오늘 로그 파일 생성 (기존 로그 파일 덮어쓰기)
with open(log_file_name, 'w', encoding='utf-8') as file:
    # 헤더 작성
    file.write("url,notice_status,work_status,done_time\n")
    for line in log_data:
        file.write(line + "\n")

print(f"총 {len(line)}개의 링크와 D-day 정보가 저장되었습니다. 파일: {output_file_path}")

# S3에 업로드
def upload_to_s3(file_path, bucket_name, object_name):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        print(f"파일이 S3에 업로드되었습니다: s3://{bucket_name}/{object_name}")
    except Exception as e:
        print(f"S3 업로드 실패: {e}")

# S3 버킷 및 객체 이름 설정
bucket_name = 't2jt'
s3_file_key = f"job/DE/sources/jumpit/links/{today}.log"

# 로컬 파일을 S3에 업로드
upload_to_s3(output_file_path, bucket_name, s3_file_key)

# Selenium 종료
driver.quit()

