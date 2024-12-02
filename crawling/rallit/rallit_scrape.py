import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 셀레니움 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 링크 파일에 따라 링크 리스트와 폴더 이름 설정
file_name = "de_links.txt"  # 파일명 설정 (이 부분을 변경하면 다른 직무 파일을 읽습니다)
# file_name = "da_links.txt"
# file_name = "be_links.txt"
# file_name = "fe_links.txt"
# file_name = "ml_links.txt"

# 링크 파일 읽기
with open(file_name, "r") as file:
    all_links = [line.strip() for line in file.readlines()]

# it_jobs 디렉토리 확인 및 생성
if not os.path.exists("it_jobs"):
    os.makedirs("it_jobs")

# 직무에 맞는 폴더 생성
if "da_links.txt" in file_name:
    job_directory = "it_jobs/da_employ"
elif "de_links.txt" in file_name:
    job_directory = "it_jobs/de_employ"
elif "be_links.txt" in file_name:
    job_directory = "it_jobs/be_employ"
elif "fe_links.txt" in file_name:
    job_directory = "it_jobs/fe_employ"
elif "ml_links.txt" in file_name:
    job_directory = "it_jobs/ml_employ"
else:
    job_directory = "it_jobs/other_employ"

# 직무별 폴더 생성
if not os.path.exists(job_directory):
    os.makedirs(job_directory)

# 각 링크에서 페이지 열고 스크랩_ 
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
        
        # 파일 경로 설정 (직무별 폴더 안에 저장)
        file_path = os.path.join(job_directory, f"{position_number}.txt")
        
        # URL을 파일의 첫 번째 줄에 추가하고, 이후에 직무 정보 추가
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"URL: {url}\n")  # URL을 첫 번째 줄에 추가
            file.write(job_content_text)  # 직무 정보 텍스트 추가
        
        print(f"Saved job content for {url} to {file_path}")
    
    except Exception as e:
        print(f"Error in processing {url}: {e}")

# 브라우저 종료
driver.quit()
