from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# 셀레니움 웹 드라이버 설정
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 시작 URL (첫 페이지 URL)
base_url = "https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword=%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%97%94%EC%A7%80%EB%8B%88%EC%96%B4&recruitPage="
params = "&recruitSort=relation&recruitPageCount=40&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&show_applied=&quick_apply=&except_read=&ai_head_hunting=&mainSearch=n"

# 이미 저장된 링크들을 불러오기 (중복 방지)
def load_existing_links():
    try:
        with open("links.txt", "r") as file:
            existing_links = set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        existing_links = set()
    return existing_links

# 링크를 파일에 저장하기
def save_links(all_links):
    with open("links.txt", "a") as file:
        for url in all_links:
            file.write(url + "\n")

# 페이지 크롤링 함수
def scrape_links():
    all_links = set()  # 새로 크롤링한 링크 저장
    existing_links = load_existing_links()  # 기존 링크 불러오기

    page_number = 1  # 첫 페이지 번호
    while True:
        # 페이지 열기
        url = f"{base_url}{page_number}{params}"
        driver.get(url)
        time.sleep(3)  # 페이지 로딩 대기

        # "검색어를 다시 확인해주세요." 메시지 확인
        try:
            container = driver.find_element(By.ID, "container")
            if "검색어를 다시 확인해주세요." in container.text:
                print(f"No results on page {page_number}. Stopping.")
                break  # 메시지가 발견되면 종료
        except Exception as e:
            # 메시지가 없으면 계속 진행
            print(f"Page {page_number}: No stopping message. Continuing...")

        # <a> 태그를 찾아 href 속성 추출
        links = driver.find_elements(By.TAG_NAME, "a")
        new_links_found = False  # 새 링크가 발견되었는지 여부를 체크

        for link in links:
            href = link.get_attribute("href")
            if href and href.startswith("https://www.saramin.co.kr/zf_user/jobs/relay/view") and href not in existing_links:
                all_links.add(href)  # 새 링크를 set에 추가
                new_links_found = True  # 새 링크가 발견되었으므로 플래그 설정

        # 새 링크가 발견되지 않았더라도 "검색결과가 없습니다" 메시지가 없으면 페이지 번호 증가
        if not new_links_found:
            print(f"No new links found on page {page_number}. Moving to next page.")

        # 페이지 번호 증가
        page_number += 1

    # 크롤링한 링크 출력
    print(f"Found {len(all_links)} new links.")

    # 중복되지 않은 링크만 저장
    if all_links:
        save_links(all_links)
        print(f"Saved {len(all_links)} new links to 'links.txt'.")
    else:
        print("No new links to save.")

# 크롤링 실행
scrape_links()

# 브라우저 종료
driver.quit()
