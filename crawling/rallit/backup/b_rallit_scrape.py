import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 셀레니움 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 'links.txt' 파일에서 링크 읽어오기
with open("links.txt", "r") as file:
    all_links = [line.strip() for line in file.readlines()]

# all_job 디렉토리 확인 및 생성
if not os.path.exists("all_jobs"):
    os.makedirs("all_jobs")

# 각 링크에서 페이지 열고 스크랩
for url in all_links:
    try:
        # 페이지 열기
        driver.get(url)
        
        # <section class="css-1h2hf16">를 기다리고 해당 내용 가져오기
        job_content_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "section.css-1h2hf16"))
        )
        
        # 섹션 내의 모든 텍스트 내용 가져오기
        job_content_text = job_content_section.text
        
        # URL에서 숫자 부분 추출 (예: https://www.rallit.com/positions/1681/ -> 1681)
        position_number = url.split('/')[-2]
        
        # 파일 경로 설정
        file_path = f"all_job/{position_number}.txt"
        
        # URL을 파일의 첫 번째 줄에 추가하고, 이후에 직무 정보 추가
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"URL: {url}\n")  # URL을 첫 번째 줄에 추가
            file.write(job_content_text)  # 직무 정보 텍스트 추가
        
        print(f"Saved job content for {url} to {file_path}")
    
    except Exception as e:
        print(f"Error in processing {url}: {e}")

# 브라우저 종료
driver.quit()