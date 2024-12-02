from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# 셀레니움 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 직무별 base_url 설정 (주석을 풀면 그 직무의 URL을 크롤링)
base_url = "https://www.rallit.com/?job=DATA_ENGINEER&jobGroup=DEVELOPER&pageNumber="  # DE
# base_url = "https://www.rallit.com/?job=DATA_ANALYST&jobGroup=DEVELOPER&pageNumber="  # DA
# base_url = "https://www.rallit.com/?job=BACKEND_DEVELOPER&jobGroup=DEVELOPER&pageNumber="  # BE 
# base_url = "https://www.rallit.com/?job=FRONTEND_DEVELOPER&jobGroup=DEVELOPER&pageNumber="  # FE
# base_url = "https://www.rallit.com/?job=MACHINE_LEARNING&jobGroup=DEVELOPER&pageNumber="  # ML

# 직무에 맞는 파일명을 동적으로 생성하는 함수
def get_file_name_from_base_url(base_url):
    if "DATA_ENGINEER" in base_url:
        return "de_links.txt"
    elif "DATA_ANALYST" in base_url:
        return "da_links.txt"
    elif "BACKEND_DEVELOPER" in base_url:
        return "be_links.txt"
    elif "FRONTEND_DEVELOPER" in base_url:
        return "fe_links.txt"
    elif "MACHINE_LEARNING" in base_url:
        return "ml_links.txt"
    else:
        return "links.txt"  # 기본 파일명

# 이미 저장된 링크들을 불러오기 (중복 방지)
def load_existing_links(file_name):
    try:
        with open(file_name, "r") as file:
            existing_links = set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        existing_links = set()
    return existing_links

# 링크를 파일에 저장하기
def save_links(all_links, file_name):
    with open(file_name, "a") as file:
        for url in all_links:
            file.write(url + "\n")

# 페이지 크롤링 함수
def scrape_links():
    all_links = set()  # 새로 크롤링한 링크 저장
    file_name = get_file_name_from_base_url(base_url)  # 직무에 맞는 파일명 설정
    existing_links = load_existing_links(file_name)  # 기존 링크 불러오기

    page_number = 1  # 첫 페이지 번호
    while True:
        # 페이지 열기
        url = f"{base_url}{page_number}"
        driver.get(url)
        time.sleep(3)  # 페이지 로딩 대기

        # 검색 결과가 없으면 종료
        try:
            no_results_message = driver.find_element(By.CSS_SELECTOR, "h2.css-8ecloi")
            if "검색결과가 없어요" in no_results_message.text:
                print(f"No results on page {page_number}. Stopping.")
                break  # 검색결과가 없으면 종료
        except Exception as e:
            # 검색결과 메시지가 없으면 정상적으로 링크 수집 진행
            print("No error found in results message.")
        
        # <a> 태그를 찾아 href 속성 추출
        links = driver.find_elements(By.TAG_NAME, "a")
        new_links_found = False  # 새 링크가 발견되었는지 여부를 체크

        for link in links:
            href = link.get_attribute("href")
            if href and href.startswith("https://www.rallit.com/positions") and href not in existing_links:
                all_links.add(href)  # 새 링크를 set에 추가
                new_links_found = True  # 새 링크가 발견되었으므로 플래그 설정

        # 새 링크가 발견되지 않았더라도 "검색결과가 없어요" 메시지가 없으면 페이지 번호 증가
        if not new_links_found:
            print(f"No new links found on page {page_number}. Moving to next page.")

        # 페이지 번호 증가 (검색결과가 없으면 페이지를 넘김)
        page_number += 1

    # 크롤링한 링크 출력
    print(f"Found {len(all_links)} new links.")

    # 중복되지 않은 링크만 저장
    if all_links:
        save_links(all_links, file_name)
        print(f"Saved {len(all_links)} new links to '{file_name}'.")
    else:
        print("No new links to save.")

# 크롤링 실행
scrape_links()

# 브라우저 종료
driver.quit()
