from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from zoneinfo import ZoneInfo
import boto3
import pymysql
import random
import re
import requests
import time
import uuid

kst = ZoneInfo("Asia/Seoul")

# AWS S3 클라이언트 설정
s3 = boto3.client('s3')

# 변수 설정 : 링크 저장을 위한 S3
BUCKET_NAME = 't2jt'
S3_LINK_PATH = 'job/{abb}/airflow_test/rocketpunch/links/'
S3_TEXT_PATH = 'job/{abb}/airflow_test/rocketpunch/txt/'
S3_IMAGE_PATH = 'job/{abb}/airflow_test/rocketpunch/images/'  

# MySQL 연결 설정
connection = pymysql.connect(
    host='43.201.40.223',
    user='user',
    password='1234',
    database='testdb',
    port=3306
)
cursor = connection.cursor()

# 변수 설정 : 검색 키워드
job_titles = {
    "DE":"데이터 엔지니어", 
    "DA":"데이터 분석가", 
    "FE":"프론트엔드 엔지니어", 
    "BE":"백엔드 엔지니어", 
    "MLE":"머신러닝 엔지니어"
}

# User-Agent 문자열
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"

chrome_options = Options()
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--headless")  # Headless 모드
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
chrome_options.add_argument("--no-sandbox")  # 리소스 제약 없는 환경에서 실행

# Selenium 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 페이지 크롤링 함수
def get_job_posts(link, job_title, s3_text_path, s3_image_path):
    try:
        # 링크에서 텍스트 크롤링
        print(f"해당 링크: {link}에서 채용공고 상세 크롤링 진행중")
        driver.get(link)
        time.sleep(random.uniform(1, 2))  # 페이지 로딩 1 ~ 2초 대기

        # 스크롤 내려서 로그인 팝업 뜨도록 설정
        previous_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 스크롤을 일정 간격으로 내리기
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 새로운 페이지 높이를 가져오기
            new_height = driver.execute_script("return document.body.scrollHeight")
            # 이전 높이와 새 높이가 같으면 더 이상 스크롤할 필요가 없으므로 종료
            if new_height == previous_height:
                break
            previous_height = new_height  # 이전 높이 업데이트

        # 로그인 팝업창 닫기 버튼 클릭
        try:
            close_popup_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[13]/div/i'))
            )
            close_popup_button.click()
            #print("팝업창 닫기 버튼 클릭 성공")
        except Exception as e:
            print("팝업창이 없거나 닫기 버튼을 찾을 수 없습니다.")


        ## 더보기 버튼 1
        try:
            more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(3) > div > a'))
            )
            actions = ActionChains(driver)
            actions.move_to_element(more_button).click().perform()
            #print("첫번째 더보기를 감지하고 눌렀습니다")
        except Exception as e:
            pass

        ## 더보기 버튼 2
        try:
            more_button2 = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(7) > div.content.break > a'))
            )
            actions2 = ActionChains(driver)
            actions2.move_to_element(more_button2).click().perform()
            #print("두번째 더보기를 감지하고 눌렀습니다")
        except Exception as e:
            pass

        ## 더보기 버튼 2.5
        try:
            more_button3 = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(7) > div > a'))
            )
            actions3 = ActionChains(driver)
            actions3.move_to_element(more_button3).click().perform()
            #print("세번째 더보기를 감지하고 눌렀습니다")
        except Exception as e:
            pass

        # due_type, due_date 크롤링에서 긁어오기
        try:
            deadline_element = WebDriverWait(driver, 10).until(   
                EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > div.four.wide.job-infoset.column > div.ui.celled.grid > div:nth-child(3) > div > div:nth-child(6) > div.content'))
            )
            deadline = deadline_element.text
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
                due_type = "날짜"
                due_date = datetime.strptime(deadline, "%Y-%m-%d").strftime("%Y-%m-%d")
            else:
                # due_type = deadline
                due_type = deadline[:20] if len(deadline.encode('utf-8')) <= 20 else deadline.encode('utf-8')[:20].decode('utf-8', 'ignore')
                due_date = None
        except Exception as e:
            print("마감 기한을 찾을 수 없습니다. 해당 요소가 로드되지 않았습니다:", e)
            due_type = "unknown"
            due_date = None
        
        # 회사 이름 요소 감지
        try:
            company_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'nowrap.company-name'))
            )
            company_name = company_element.text
        except Exception as e:
            company_name = "unknown"
            print("회사 이름을 찾을 수 없습니다:", e)
        
        # 공고 제목 요소 감지
        try:
            post_title_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > div.four.wide.job-infoset.column > div.ui.celled.grid > div:nth-child(3) > h2'))
            )
            post_title = post_title_element.text
        except Exception as e:
            post_title = "unknown"
            print("공고 제목을 찾을 수 없습니다:", e)

        # 여기서 부터 공고에서 텍스트, 이미지 감지 > 텍스트와 이미지 s3에 저장후 url 반환
        div_selectors = [
            '#wrap > div.eight.wide.job-content.column > section:nth-child(3)',   # 주요업무
            '#wrap > div.eight.wide.job-content.column > section:nth-child(5)',   # 업무기술/활동분야
            '#wrap > div.eight.wide.job-content.column > section:nth-child(7)',   # 채용상세
            '#wrap > div.eight.wide.job-content.column > section:nth-child(11)'   # 산업분야
        ]  
        # process_content에서 notice_type, text, image 탐지하고 text, image는 바로 s3에 저장
        # 그리고 저장된 각각의 s3의 주소를 반환
        notice_type, image_paths, text_path = process_contents(div_selectors, s3_text_path, s3_image_path)
        s3_images_url = ",".join(image_paths) if image_paths else None

        create_time = update_time = datetime.now(tz=kst).strftime("%Y-%m-%d %H:%M:%S") 
        job_post = {
            'create_time': create_time,
            'update_time': update_time,
            'removed_time': None,
            'site': 'rocketpunch',
            'job_title': job_title,  # 동적으로 받아온 job_title 사용
            'due_type': due_type,
            'due_date': due_date,
            'company': company_name,
            'post_title': post_title,
            'notice_type': notice_type,
            'org_url': link,
            's3_text_url': text_path,
            's3_images_url': s3_images_url,
            'responsibility': None,
            'qualification': None,
            'preferential': None
        }
        
        query = """
        INSERT INTO airflowT (create_time, update_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url)
        VALUES (%(create_time)s, %(update_time)s, %(site)s, %(job_title)s, %(due_type)s, %(due_date)s, %(company)s, 
                %(post_title)s, %(notice_type)s, %(org_url)s, %(s3_text_url)s, %(s3_images_url)s);
        """
        cursor.execute(query, job_post)
        connection.commit()

    except Exception as e:
        print(f"❌ 데이터 삽입 실패 (job_post: {job_post.get('org_url')}): {str(e)}")
    finally:
        driver.quit()
    
# 이 안에서 S3 method import 피일보내고 url 반환 / db method 메타데이터 보내고 url도 입력
# for loop 마다 db로 보내면 중간
def process_contents(div_selectors, s3_text_path, s3_image_path):
    """
    지정된 CSS Selectors에서 텍스트와 이미지를 탐지하여 최종 notice_type 값을 반환하고,
    탐지된 이미지를 로컬 디렉토리에 다운로드하며 텍스트는 하나로 묶어 로컬에 저장.
    """
    all_image_urls = []  # 모든 섹션의 이미지 URL 저장
    all_texts = []  # 모든 섹션의 텍스트 저장
    final_notice_type = "none"  # 초기값 설정

    for selector in div_selectors:
        try:
            # 섹션 가져오기
            section = driver.find_element(By.CSS_SELECTOR, selector)

            # 텍스트 탐지
            section_text = section.text.strip() if section.text else None
            if section_text:
                all_texts.append(section_text)

            # 이미지 탐지
            image_elements = section.find_elements(By.TAG_NAME, "img")
            section_image_urls = [img.get_attribute("src") for img in image_elements if img.get_attribute("src")]
            all_image_urls.extend(section_image_urls)
            
            # notice_type 업데이트
            if section_text and section_image_urls:
                final_notice_type = "both"
            elif section_text and final_notice_type != "both":
                final_notice_type = "text"
            elif section_image_urls and final_notice_type not in ["both", "text"]:
                final_notice_type = "image"
        except Exception as e:
            print(f"CSS Selector {selector} 처리 중 에러 발생: {e}")

    # 텍스트 파일 저장
    combined_text = "\n".join(all_texts)
    uploaded_text_path = upload_text_to_s3(s3_text_path, combined_text)

    # 이미지 다운로드
    uploaded_image_paths = upload_image_to_s3(s3_image_path, all_image_urls)

    return final_notice_type, uploaded_image_paths, uploaded_text_path

def upload_text_to_s3(s3_text_path, texts):
    """ 텍스트를 S3에 업로드하고 URL을 반환하는 함수 """
    text_uuid = str(uuid.uuid4())  # UUID 생성
    text_key = f"{s3_text_path}{text_uuid}.txt"  # S3에 저장할 경로 및 파일명
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=text_key, Body=texts)
        text_url = f"s3://{BUCKET_NAME}/{text_key}"
        print(f"✅ 파일 {text_key}가 성공적으로 S3 {text_url}에 업데이트 되었습니다")
        return text_url
    except Exception as e:
        print(f"⛔ [ERROR] Failed to upload text to S3: {e}")
        return None

def upload_image_to_s3(s3_image_path, image_urls):
    """ 이미지 URL 리스트를 받아 이미지를 S3에 업로드하고 S3 URL 리스트를 반환하는 함수 """
    s3_urls = []  # 업로드된 S3 URL을 저장할 리스트

    for image_url in image_urls:
        try:
            # 이미지 다운로드
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # 다운로드 오류 시 예외 발생
            # UUID로 고유 이름 생성
            image_uuid = str(uuid.uuid4())
            image_key = f"{s3_image_path}{image_uuid}.jpg"
            # S3에 업로드
            s3.upload_fileobj(response.raw, BUCKET_NAME, image_key)
            # 업로드된 S3 URL 생성
            s3_url = f"s3://{BUCKET_NAME}/{image_key}"
            s3_urls.append(s3_url)

        except Exception as e:
            print(f"⛔ [ERROR] 이미지 업로드 실패 ({image_url}): {e}")

    # 콤마로 연결된 S3 URL 반환
    print(f"✅ 이미지 파일(들)이 성공적으로 S3 {s3_image_path}에 업데이트 되었습니다")
    return s3_urls

def get_latest_txt_files(s3_link_path):
    # 모든 파일 리스트 가져오기 (ContinuationToken 활용)
    files = []
    continuation_token = None
    while True:
        params = {'Bucket': BUCKET_NAME, 'Prefix': s3_link_path}
        if continuation_token:
            params['ContinuationToken'] = continuation_token
        response = s3.list_objects_v2(**params)

        # s3 path 에 파일이 아예 없을 경우 처리
        if 'Contents' not in response:
            print(f"[ERROR] 해당 S3 path에 파일이 존재하지 않습니다: {s3_link_path}")
            return None
        # 파일 리스트에 추가
        files.extend(response['Contents'])

        # 다음 페이지로 넘어갈 ContinuationToken 확인
        continuation_token = response.get('NextContinuationToken')
        if not continuation_token:
            break
    
    # txt 파일 리스트 가져오기
    txt_files = [content['Key'] for content in files if content['Key'].endswith('.txt')]
    if not txt_files:
        print("No .txt files found in the specified directory.")
        return []
    
    # 파일명에서 날짜 추출 후 정렬
    txt_files.sort(key=lambda x: datetime.strptime(x.split('/')[-1].split('.')[0], '%Y%m%d'))
    # 최신 파일 1개 또는 2개 가져오기
    latest_files = txt_files[-2:] if len(txt_files) > 1 else txt_files
    # 최신 파일 2개의 내용 가져오기
    file_contents = []
    for file_key in latest_files:
        try:
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
            file_content = obj['Body'].read().decode('utf-8')
            file_contents.append(file_content)
        except Exception as e:
            print(f"[ERROR] 파일을 가져오는 중 오류가 발생했습니다. 파일 키: {file_key}, 에러: {e}")
    return file_contents

def update_removed_links_in_db(removed_links, connection):
    try:
        if not connection.open:
            connection.ping(reconnect=True)  # 연결이 닫혀있다면 재연결 시도
        for link in removed_links:
            sql = """
            UPDATE airflowT SET removed_time = %s WHERE org_url = %s
            """
            cursor.execute(sql, (datetime.today().strftime("%Y-%m-%d"), link))
        connection.commit()
        print(f"Updated removed links in DB: {len(removed_links)}")
    except Exception as e:
        print(f"Error updating removed links in DB: {e}")

# 메인 메소드
def main():
    try:
        if not connection.open:
            print("❌ 데이터베이스 연결에 실패했습니다. 연결을 확인하세요.")
            return
        
        for job_abb, job_title in job_titles.items():
            s3_link_path = S3_LINK_PATH.format(abb = job_abb)
            s3_text_path = S3_TEXT_PATH.format(abb = job_abb) # s3 텍스트 저장 경로 설정
            s3_image_path = S3_IMAGE_PATH.format(abb = job_abb) # s3 이미지 저장 경로 설정

            # s3안에 어제 오늘 링크 가지고 오기
            latest_contents = get_latest_txt_files(s3_link_path)
            if len(latest_contents) == 0:
                print(f"{job_title}: You need to crawl the links first")

            elif len(latest_contents) == 1:
                # s3에 오늘 크롤링한 리스트만 있을때
                today_list = latest_contents[0].splitlines()
                for url in today_list:
                    get_job_posts(url, job_title, s3_text_path, s3_image_path)
                print(f"[CHECKING] 오늘 크롤링한 공고의 개수: {len(today_list)}개")
            elif len(latest_contents) == 2:
                # "url1\nurl2\nurl3" 형식으로 나오므로 list로 변환
                yesterday_list = latest_contents[0].splitlines()
                today_list = latest_contents[-1].splitlines()
                print(f"{job_title}: {s3_link_path}로부터 오늘공고 {len(today_list)}개, 어제 공고 {len(yesterday_list)}개")

                # today_list에는 있지만 yesterday_list에는 없는 URL 리스트
                only_in_today = list(set(today_list) - set(yesterday_list))
                for url in only_in_today:
                    get_job_posts(url, job_title, s3_text_path, s3_image_path)
                print(f"[CHECKING] 오늘 크롤링한 공고의 개수: {len(only_in_today)}개")

                # yesterday_list에는 있지만 today_list에는 없는 URL 리스트
                only_in_yesterday = list(set(yesterday_list) - set(today_list))
                update_removed_links_in_db(only_in_yesterday, connection)
            else:
                # 이론적으로는 len(latest_contents)가 0, 1, 2 이외의 값을 가질 수 없음
                print(f"{job_title}: Unexpected number of files found.")
            
            # 그리고 저장된 path json으로 받아와서 db에 전부 업데이트 - dbmethod
            print(f"🌟{job_title}에 대한 크롤링과 DB업데이트를 완료하였습니다!")

        print("✅ 모든 데이터 삽입 및 업데이트가 성공했습니다!")
    except Exception as e:
        print(f"Unexpected error during main execution: {e}")
    finally:
        driver.quit()
        cursor.close()
        connection.close()


if __name__=="__main__":
    main()