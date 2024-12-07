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
    try:
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=s3_key)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        print(f"Error fetching S3 file {s3_key}: {e}")
        return ""

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
    
    pattern = re.compile(rf"^(?:\s*)({start_pattern})(?:\s*)\n([\s\S]+?)(?=\n(?:\s*)({end_pattern})(?:\s*)|\Z)", re.MULTILINE)
    
    match = pattern.search(text)
    
    if match:
        return match.group(2).strip()  # 추출된 텍스트 반환
    else:
        return None

# DB에서 URL 값 추출
def get_s3_urls_from_db():
    cursor = connection.cursor()
    
    query = """
        SELECT id, s3_text_url 
        FROM wanted
        WHERE 
            ((responsibility IS NULL) + (qualification IS NULL) + (preferential IS NULL)) >= 2
            AND site = 'wanted'
    """
    
    cursor.execute(query)
    urls = cursor.fetchall()
    return urls  # [(id, s3_text_url)] 형식의 리스트 반환

# DB 업데이트 쿼리 함수
def update_job_info_in_db(job_id, key_tasks, requirements, preferred_qualifications):
    cursor = connection.cursor()

    # None 값을 NULL로 변환
    key_tasks = key_tasks if key_tasks else None
    requirements = requirements if requirements else None
    preferred_qualifications = preferred_qualifications if preferred_qualifications else None

    update_query = """
    UPDATE wanted 
    SET responsibility = %s, qualification = %s, preferential = %s 
    WHERE id = %s
    """
    cursor.execute(update_query, (key_tasks, requirements, preferred_qualifications, job_id))
    
# 섹션 추출 설정
sections_to_extract = {
    "주요업무": {
        "start_titles": ["주요업무"],
        "end_titles": ["자격요건", "▶ 서류전형 ▶ 면접전형 ▶ 건강검진 ▶ 최종합격"]
    },
    "자격요건": {
        "start_titles": ["자격요건"],
        "end_titles": ["우대사항", "혜택 및 복지"]
    },
    "우대사항": {
        "start_titles": ["우대사항"],
        "end_titles": ["혜택 및 복지"]
    }
}
# DB에서 URL 목록을 가져오기
s3_urls = get_s3_urls_from_db()

# MySQL 커서 한 번만 생성
cursor = connection.cursor()

# 각 URL에 대해 텍스트 파일을 읽고 섹션을 추출
for job_id, url in s3_urls:
    try:
        bucket_name, s3_key = extract_s3_details(url)
        job_description = get_s3_file_content(bucket_name, s3_key)

        key_tasks = extract_section(sections_to_extract["주요업무"]["start_titles"], sections_to_extract["주요업무"]["end_titles"], job_description) or ""
        requirements = extract_section(sections_to_extract["자격요건"]["start_titles"], sections_to_extract["자격요건"]["end_titles"], job_description) or ""
        preferred_qualifications = extract_section(sections_to_extract["우대사항"]["start_titles"], sections_to_extract["우대사항"]["end_titles"], job_description) or ""

        print(f"Responsibility length: {len(key_tasks) if key_tasks else 0}")
        print(f"Qualification length: {len(requirements) if requirements else 0}")
        print(f"Preferential length: {len(preferred_qualifications) if preferred_qualifications else 0}")

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

# MySQL 커밋 및 종료
connection.commit()
connection.close()
