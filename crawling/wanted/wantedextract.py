import pymysql
import boto3
import re

# MySQL 연결 설정
connection = pymysql.connect(
    host='43.201.40.223',
    user='user',
    password='1234',
    database='testdb',
    port=3306
)

# S3에서 텍스트 파일을 읽어오는 함수
def get_s3_file_content(bucket_name, s3_key):
    s3 = boto3.client('s3')  # S3 클라이언트 생성
    response = s3.get_object(Bucket=bucket_name, Key=s3_key)
    file_content = response['Body'].read().decode('utf-8')  # UTF-8로 디코딩하여 텍스트로 읽음
    return file_content

# S3 URL에서 버킷명과 객체 키 추출
def extract_s3_details(s3_url):
    url_parts = s3_url[5:].split('/', 1)  # 's3://' 부분을 제거하고, 첫 번째 '/'로 분리
    bucket_name = url_parts[0]
    s3_key = url_parts[1]
    return bucket_name, s3_key

# 섹션 추출 함수
def extract_section(start_titles, end_titles, text):
    start_pattern = '|'.join([re.escape(start) for start in start_titles])
    end_pattern = '|'.join([re.escape(end) for end in end_titles])
    
    # 정규 표현식으로 시작과 끝을 찾아서 그 사이의 텍스트 추출
    pattern = re.compile(rf"^(?:\s*)({start_pattern})(?:\s*)\n([\s\S]+?)(?=\n(?:\s*)({end_pattern})(?:\s*)|\Z)", re.MULTILINE)
    
    match = pattern.search(text)
    
    if match:
        return match.group(2).strip()  # 추출된 텍스트 반환
    else:
        return None

# DB에서 URL 값 추출 (responsibility, qualification, preferential 중 2개가 NULL인 경우)
def get_s3_urls_from_db():
    cursor = connection.cursor()
    
    # responsibility, qualification, preferential 컬럼 중 2개가 NULL인 경우의 URL만 추출
    query = """
        SELECT id, s3_text_url 
        FROM wanted
        WHERE 
            (responsibility IS NULL AND qualification IS NULL) OR
            (responsibility IS NULL AND preferential IS NULL) OR
            (qualification IS NULL AND preferential IS NULL)
    """
    
    cursor.execute(query)
    urls = cursor.fetchall()
    return urls  # [(id, s3_text_url)] 형식의 리스트 반환

# 섹션 추출 설정
sections_to_extract = {
    "주요업무": {
        "start_titles": ["주요업무"],
        "end_titles": ["자격요건","▶ 서류전형 ▶ 면접전형 ▶ 건강검진 ▶ 최종합격","[연봉]","【 이런 팀에서 일해요 】","[클럼엘의 채용 절차]","[커리어 비전]","[합류시, 이런 성장의 기회를 만나볼 수 있어요.]","[합류 시, 이런 성장의 기회를 만나볼 수 있어요.]","■ 이런 절차로 채용합니다","[ 근무 조건 ]","[합류 시, 이런 성장의 기회를 만나볼 수 있어요.]"]
    },
    "자격요건": {
        "start_titles": ["자격요건"],
        "end_titles": ["우대사항","혜택 및 복지","일반적인 전형 과정","* 필수 제출서류/자유양식","[몰입할 수 있는 최고의 환경]"]
    },
    "우대사항": {
        "start_titles": ["우대사항"],
        "end_titles": ["혜택 및 복지","오해 없도록 주의","＜ 채용절차 ＞","[이런 고민을 하며 나아갑니다]","[ ML Research Team은 이런 팀입니다 ]","[합류 여정]","[근무지]","[핵클이 사용하는 기술]","[채용절차]","[자주 묻는 질문]","【 이렇게 합류하게 돼요 】","■ 정규직 : 셰어라운드의 문화와 비전에 맞는지 확인하기 위해 6개월 수습기간 있음","[ 함께 일하고 싶은 동료의 모습입니다. ]","[동료의 한마디]","[기타사항]","[이력서는 이렇게 작성하시는 걸 추천해요]","■ 지원시 참고하실 사항","• 본 공고는 수시채용으로 진행되며, 채용 완료 시 조기에 마감될 수 있습니다.","[데이터 플랫폼 챕터는 이렇게 일하고 있어요.]","[공통 지원자격]","[삼쩜삼 데이터 분석 챕터는 이렇게 일하고 있어요.]","모든 직군 채용합니다.","[삼쩜삼 데이터 플랫폼 챕터는 이렇게 일하고 있어요.]"]
    }
}

# DB에서 URL 목록을 가져오기
s3_urls = get_s3_urls_from_db()

# MySQL 업데이트 쿼리 함수
def update_job_info_in_db(job_id, key_tasks, requirements, preferred_qualifications):
    cursor = connection.cursor()
    
    update_query = """
    UPDATE wanted 
    SET responsibility = %s, qualification = %s, preferential = %s 
    WHERE id = %s
    """
    cursor.execute(update_query, (key_tasks, requirements, preferred_qualifications, job_id))
    connection.commit()

# 각 URL에 대해 텍스트 파일을 읽고 섹션을 추출
for job_id, url in s3_urls:
    try:
        bucket_name, s3_key = extract_s3_details(url)
        job_description = get_s3_file_content(bucket_name, s3_key)

        key_tasks = extract_section(sections_to_extract["주요업무"]["start_titles"], sections_to_extract["주요업무"]["end_titles"], job_description)
        requirements = extract_section(sections_to_extract["자격요건"]["start_titles"], sections_to_extract["자격요건"]["end_titles"], job_description)
        preferred_qualifications = extract_section(sections_to_extract["우대사항"]["start_titles"], sections_to_extract["우대사항"]["end_titles"], job_description)
        print(f"Responsibility length: {len(key_tasks)}")
        print(f"Qualification length: {len(requirements)}")
        print(f"Preferential length: {len(preferred_qualifications)}")

        # 추출된 정보를 DB에 업데이트
        update_job_info_in_db(job_id, key_tasks, requirements, preferred_qualifications)

        # 출력
        print(f"URL: {url}")
        print(f"주요업무: {key_tasks}")
        print(f"자격요건: {requirements}")
        print(f"우대사항: {preferred_qualifications}")
        print("=" * 50)

    except Exception as e:
        print(f"Error processing URL {url}: {e}")

connection.close()


# 최소 2개의 칼럼이 null 인 경우의 url만 긁어와서 전처리 하도록 설정
