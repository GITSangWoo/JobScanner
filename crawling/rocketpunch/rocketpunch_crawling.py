from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime as dt
from zoneinfo import ZoneInfo

from s3_methods import upload_text_to_s3, upload_image_to_s3
import random
import re
import time

# User-Agent 문자열
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36"

chrome_options = Options()
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--headless")  # Headless 모드
chrome_options.add_argument("--disable-gpu")  # GPU 비활성화
chrome_options.add_argument("--no-sandbox")  # 리소스 제약 없는 환경에서 실행

kst = ZoneInfo("Asia/Seoul")

def get_job_posts(bucket, links_added, job_title, s3_text_path, s3_image_path):
    """
    수집한 채용공고의 링크에서 공고텍스트를 가져오는 함수
    :param json_filepath: JSON 파일 경로 (링크 리스트가 저장된 파일)
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    job_posts = []

    # 링크에서 텍스트 크롤링
    for link in links_added:
        job_post = {} # 링크 하나 당 결과 저장용 딕셔너리
        print(f"해당 링크: {link}에서 채용공고 상세 크롤링 진행중")
        driver.get(link)
        time.sleep(random.uniform(1, 3))  # 페이지 로딩 1 ~ 3초 대기

        # 스크롤 내려서 로그인 팝업 뜨도록 설정
        previous_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # 스크롤을 일정 간격으로 내리기
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)  # 페이지 로딩 대기

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
            print("팝업창 닫기 버튼 클릭 성공")
        except Exception as e:
            print("팝업창이 없거나 닫기 버튼을 찾을 수 없습니다.")

        # "상세 정보 더 보기" 클릭 요소 css.selector로 찾기
        ## 더보기 버튼 1
        try:
            more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(3) > div > a'))
            )
            actions = ActionChains(driver)
            actions.move_to_element(more_button).click().perform()
            print("첫번째 더보기를 감지하고 눌렀습니다")
        except Exception as e:
            pass

        ## 더보기 버튼 2
        try:
            more_button2 = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(7) > div.content.break > a'))
            )
            actions2 = ActionChains(driver)
            actions2.move_to_element(more_button2).click().perform()
            print("두번째 더보기를 감지하고 눌렀습니다")
        except Exception as e:
            pass

        ## 더보기 버튼 2.5
        try:
            more_button3 = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#wrap > div.eight.wide.job-content.column > section:nth-child(7) > div > a'))
            )
            actions3 = ActionChains(driver)
            actions3.move_to_element(more_button3).click().perform()
            print("세번째 더보기를 감지하고 눌렀습니다")
        except Exception as e:
            pass

        # 상세 내용 섹션 가져오기
        current_time = dt.now(tz=kst)
        # id_count += 1
        # job_post["id"] = id_count / db에 넣을 때는 auto increment라서 여기서 지정안해야 할 듯
        job_post["create_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S") 
        job_post["update_time"] = current_time.strftime("%Y-%m-%d %H:%M:%S") 
        job_post["removed_time"] = None
        job_post["site"] = "rocketpunch" 
        job_post["job_title"] = job_title
        # due_type, due_date 크롤링에서 긁어오기
        try:
            deadline_element = WebDriverWait(driver, 10).until(   
                EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > div.four.wide.job-infoset.column > div.ui.celled.grid > div:nth-child(3) > div > div:nth-child(6) > div.content'))
            )
            deadline = deadline_element.text
            date_pattern = r"\d{4}-\d{2}-\d{2}"
            if re.fullmatch(date_pattern, deadline):
                job_post["due_type"] = "날짜"
                job_post["due_date"] = dt.strptime(deadline, "%Y-%m-%d").strftime("%Y-%m-%d")
            else:
                job_post["due_type"] = deadline
                job_post["due_type"] = deadline[:20] if len(deadline.encode('utf-8')) <= 20 else deadline.encode('utf-8')[:20].decode('utf-8', 'ignore')
                job_post["due_date"] = None
        except Exception as e:
            print("마감 기한을 찾을 수 없습니다. 해당 요소가 로드되지 않았습니다:", e)
            job_post["due_type"] = "unknown"
            job_post["due_date"] = None
        
        # 회사 이름 요소 감지
        try:
            company_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'nowrap.company-name'))
            )
            job_post["company"] = company_element.text
        except Exception as e:
            job_post["company"] = "unknown"
            print("회사 이름을 찾을 수 없습니다:", e)
        
        # 공고 제목 요소 감지
        try:
            post_title_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '#wrap > div.four.wide.job-infoset.column > div.ui.celled.grid > div:nth-child(3) > h2'))
            )
            job_post["post_title"] = post_title_element.text
        except Exception as e:
            job_post["post_title"] = "unknown"
            print("공고 제목을 찾을 수 없습니다:", e)

        # 여기서 부터 공고에서 텍스트, 이미지 감지 > 텍스트와 이미지 s3에 저장후 url 반환
        div_selectors = ['#wrap > div.eight.wide.job-content.column > section:nth-child(3)',   # 주요업무
                         '#wrap > div.eight.wide.job-content.column > section:nth-child(5)',   # 업무기술/활동분야
                         '#wrap > div.eight.wide.job-content.column > section:nth-child(7)',   # 채용상세
                         '#wrap > div.eight.wide.job-content.column > section:nth-child(11)']  # 산업분야
        
        # process_content에서 notice_type, text, image 탐지하고 text, image는 바로 s3에 저장
        # 그리고 저장된 각각의 s3의 주소를 반환
        notice_type, image_paths, text_path = process_contents(driver, div_selectors, bucket, s3_text_path, s3_image_path)

        job_post["notice_type"] = notice_type
        job_post["org_url"] = link
        job_post["s3_text_url"] = text_path
        job_post["s3_images_url"] = ",".join(image_paths) if image_paths else None
        job_post["responsibility"] = None
        job_post["qualification"] = None
        job_post["preferential"] = None

        job_posts.append(job_post)

        time.sleep(random.uniform(2, 5)) # 다음 공고 링크 접속까지 2~5초 시간 주기
    return job_posts

# 이 안에서 S3 method import 피일보내고 url 반환 / db method 메타데이터 보내고 url도 입력
# for loop 마다 db로 보내면 중간
def process_contents(driver, div_selectors, bucket, s3_text_path, s3_image_path):
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
    uploaded_text_path = upload_text_to_s3(bucket, s3_text_path, combined_text)

    # 이미지 다운로드
    uploaded_image_paths = upload_image_to_s3(bucket, s3_image_path, all_image_urls)

    return final_notice_type, uploaded_image_paths, uploaded_text_path