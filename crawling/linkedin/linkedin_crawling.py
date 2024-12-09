from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# Chrome옵션 설정
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")  # 브라우저 UI를 표시하지 않으려면 이 줄을 추가

# webdriver 설정
driver = webdriver.Chrome(options=chrome_options)

try:
    # 웹 페이지 열기
    driver.get("https://www.google.com")  # 크롤링할 URL로 변경

    # 페이지의 제목 가져오기
    title = driver.title
    print(f"Page Title: {title}")

finally:
    # 브라우저 닫기
    driver.quit()