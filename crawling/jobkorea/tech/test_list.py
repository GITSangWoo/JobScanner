import re
import json

# 기술 관련 키워드를 포함하는 tech_book.json 파일 경로
tech_file_path = 'tech_book.json'

# tech_book.json 파일을 읽어서 기술 스택과 키워드를 가져오는 함수
def load_tech_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        tech_keywords = json.load(file)
    return tech_keywords

# 기술 스택을 식별하는 함수
def identify_tech_stack(text, tech_keywords):
    identified_tech = {}
    
    for tech, keywords in tech_keywords.items():
        # 키워드 목록을 하나의 정규 표현식으로 합침
        pattern = r'(?i)(?:' + '|'.join(map(re.escape, keywords)) + r')'
        matches = re.findall(pattern, text)  # 대소문자 구분하지 않음
        
        if matches:
            identified_tech[tech] = matches  # 기술 및 관련 키워드를 기록
            
    return identified_tech

# 텍스트에서 불필요한 공백을 제거하는 함수
def clean_text(text):
    # 여러 공백을 하나의 공백으로 바꿔줌
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    return cleaned_text

# 로컬 파일에서 테스트할 텍스트를 가져오는 함수
def load_local_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# 로컬 파일 텍스트로 기술 스택을 식별하는 함수
def process_local_text(file_path):
    tech_keywords = load_tech_keywords(tech_file_path)
    text = load_local_text(file_path)  # 로컬 파일에서 텍스트 읽기

    print(f"\n[텍스트]\n")
    print(f"{text}\n")
    
    # 텍스트에서 줄 바꿈 문자(\n, \r)를 제거하고 한 줄로 만들기
    re_text = re.sub(r'[\r\n]+', ' ', text).strip()

    # 공백 처리만 하고 특수문자는 그대로 유지
    cleaned_text = clean_text(re_text)

    # 기술 스택 식별
    identified_tech = identify_tech_stack(cleaned_text, tech_keywords)

    # 결과 출력
    if identified_tech:
        print("\n[식별된 기술 스택]\n")
        for key, value in identified_tech.items():
            print(f"{key}")
            print(value)
    else:
        print("\n식별된 기술 스택이 없습니다.")

# 테스트할 로컬 텍스트 파일 경로
local_text_file_path = 'test.txt'

# 실제 로컬 파일 텍스트 처리 실행
process_local_text(local_text_file_path)
