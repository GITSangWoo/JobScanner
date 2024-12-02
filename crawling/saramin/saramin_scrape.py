import os
import re
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

# all_jobs 디렉토리 확인 및 생성
if not os.path.exists("all_jobs"):
    os.makedirs("all_jobs")

# 각 링크에서 페이지 열고 스크랩
for url in all_links:
    try:
        print(f"Processing URL: {url}")  # 디버깅 메시지
        # URL에서 idx 값 추출
        match = re.search(r"idx=(\d+)", url)
        if not match:
            print(f"No idx found in URL: {url}")
            continue
        idx_value = match.group(1)
        print(f"Extracted idx: {idx_value}")  # 추출된 idx 확인

        # 페이지 열기
        driver.get(url)
        print("Page loaded successfully.")  # 디버깅 메시지

        # iframe 전환
        try:
            iframe = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe#iframe_content_0"))
            )
            driver.switch_to.frame(iframe)
            print("Switched to iframe.")  # 디버깅 메시지
        except Exception as e:
            print(f"Error switching to iframe: {e}")
            continue

        # iframe 내부 텍스트 가져오기
        try:
            iframe_body = driver.find_element(By.TAG_NAME, "body")
            content_text = iframe_body.text.strip()
            print("Iframe text content found.")  # 디버깅 메시지
        except Exception as e:
            content_text = "No text found in iframe."
            print(f"Error finding iframe text: {e}")

        # iframe 내부 이미지 가져오기
        try:
            img_elements = iframe_body.find_elements(By.TAG_NAME, "img")
            img_links = set()
            for img in img_elements:
                src = img.get_attribute("src")
                alt = img.get_attribute("alt")
                if src:
                    img_links.add(f"Image: {alt if alt else 'No alt'} | Link: {src}")
            print("Iframe images found.")  # 디버깅 메시지
        except Exception as e:
            img_links = []
            print(f"Error finding images: {e}")

        # iframe에서 메인 페이지로 복귀
        driver.switch_to.default_content()

        # 파일 저장
        file_path = f"all_jobs/{idx_value}.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"URL: {url}\n\n")
            file.write("Iframe Text Content:\n")
            file.write(content_text + "\n\n")
            if img_links:
                file.write("Iframe Image Links:\n")
                file.write("\n".join(img_links))
            else:
                file.write("No images found in iframe.\n")
        print(f"Saved job content to {file_path}")

    except Exception as e:
        print(f"Error processing URL {url}: {e}")

# 브라우저 종료
driver.quit()
