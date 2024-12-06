import boto3
import pymysql
from datetime import datetime

# S3 클라이언트 설정
s3_client = boto3.client('s3')

def list_s3_files(bucket_name, prefix):
    """S3 버킷에서 지정된 prefix(경로)에 있는 모든 파일 목록을 반환"""
    files = []
    continuation_token = None
    while True:
        params = {
            'Bucket': bucket_name,
            'Prefix': prefix
        }
        if continuation_token:
            params['ContinuationToken'] = continuation_token
        
        response = s3_client.list_objects_v2(**params)
        files.extend([content['Key'] for content in response.get('Contents', [])])
        continuation_token = response.get('NextContinuationToken')
        if not continuation_token:
            break
    return files

def extract_text_from_s3_file(bucket_name, file_key, keyword_groups):
    """S3에서 파일을 읽고 텍스트 추출"""
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read().decode('utf-8')
    
    extracted_sections = {}
    
    # 각 줄을 순차적으로 확인
    lines = file_content.splitlines()
    
    for group in keyword_groups:
        section_name = group['section_name']
        start_keywords = group['start_keywords']
        end_keywords = group['end_keywords']
        
        start_index = None
        section_text = ""
        section_started = False
        
        # 섹션 시작을 찾기 위해 한 줄씩 확인
        for line in lines:
            # start_keywords와 정확히 일치하는 경우 섹션 시작
            if not section_started:
                for start in start_keywords:
                    if line.strip() == start:  # 줄이 start_keywords 중 하나와 정확히 일치하면
                        section_started = True
                        break
            
            if section_started:
                # end_keywords를 찾은 경우 섹션 종료
                if any(end in line for end in end_keywords):
                    section_started = False
                    break
                
                # 섹션 텍스트에 추가
                section_text += line + "\n"
        
        # 섹션 텍스트가 존재하는 경우에만 추출
        if section_text.strip():
            extracted_sections[section_name] = section_text.strip()
    
    return extracted_sections

def process_and_insert_into_db(bucket_name, keyword_groups, conn):
    """S3 데이터를 처리하고 MySQL에 바로 적재"""
    cursor = conn.cursor()
    
    max_length = 1000  # 최대 길이 설정
    
    # 각 직무에 대해 처리
    job_codes = ['DE', 'FE', 'BE', 'DA', 'MLE']  # 처리할 직무 코드 목록
    for job_code in job_codes:
        prefix = f'job/{job_code}/sources/jobkorea/txt/'  # 직무별 S3 경로
        # S3 버킷에서 텍스트 파일 목록 가져오기
        files = list_s3_files(bucket_name, prefix)

        for file_key in files:
            if file_key.endswith('.txt'):  # .txt 파일만 처리
                sections = extract_text_from_s3_file(bucket_name, file_key, keyword_groups)
                full_s3_url = f"s3://{bucket_name}/{file_key}"  # S3 파일 URL 생성
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시각
                
                # 텍스트 길이 제한
                responsibility = sections.get('주요업무', '')[:max_length]
                qualification = sections.get('자격요건', '')[:max_length]
                preferential = sections.get('우대사항', '')[:max_length]
                
                # MySQL 데이터 삽입/업데이트
                cursor.execute("""
                    UPDATE jobkorea
                    SET responsibility = %s, qualification = %s, preferential = %s
                    WHERE s3_text_url = %s
                    AND (responsibility IS NULL AND qualification IS NULL AND preferential IS NULL)
                """, (responsibility, qualification, preferential, full_s3_url))
    
    conn.commit()
    cursor.close()

# 키워드 그룹 정의
keyword_groups = [
    {
        "section_name": "주요업무",
        "start_keywords": ["담당업무", "주요업무", "주요 업무"],
        "end_keywords": ["필수 자격", "필요 역량"]
    },
    {
        "section_name": "자격요건",
        "start_keywords": ["자격 요건", "필수자격"],
        "end_keywords": ["우대 사항", "우대 요건"]
    },
    {
        "section_name": "우대사항",
        "start_keywords": ["우대 사항", "우대 요건"],
        "end_keywords": ["전형 절차", "0명 "]
    }
]

# MySQL 연결 설정
conn = pymysql.connect(
    host='43.201.40.223',          # AWS 퍼블릭 IP
    user='user',                   # MySQL 사용자
    password='1234',               # MySQL 비밀번호
    database='testdb',             # 데이터베이스 이름
    charset='utf8mb4'
)

# S3 버킷과 경로 지정
bucket_name = 't2jt'

# 데이터 처리 및 MySQL로 바로 적재
process_and_insert_into_db(bucket_name, keyword_groups, conn)

# MySQL 연결 종료
conn.close()
