import re
import pymysql
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# SparkSession 초기화
spark = SparkSession.builder \
    .appName("JobInfoProcessing") \
    .getOrCreate()

# MySQL 연결 설정
def get_mysql_connection():
    return pymysql.connect(
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
    connection = get_mysql_connection()
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
    connection.close()
    
    return urls  # [(id, s3_text_url)] 형식의 리스트 반환

# DB 업데이트 함수 (Batch Insert 방식)
def update_batch_to_db(iterator):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    # 여러 데이터를 한 번에 업데이트
    batch_data = []
    for job_id, key_tasks, requirements, preferred_qualifications in iterator:
        batch_data.append((key_tasks, requirements, preferred_qualifications, job_id))

        # Batch 크기 조절 (예: 100개마다 Commit)
        if len(batch_data) >= 100:
            cursor.executemany("""
                UPDATE wanted 
                SET responsibility = %s, qualification = %s, preferential = %s 
                WHERE id = %s
            """, batch_data)
            connection.commit()
            batch_data = []  # Batch 초기화

    # 마지막 남은 데이터 처리
    if batch_data:
        cursor.executemany("""
            UPDATE wanted 
            SET responsibility = %s, qualification = %s, preferential = %s 
            WHERE id = %s
        """, batch_data)
        connection.commit()

    connection.close()

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
        "end_titles": ["혜택 및 복지","오해 없도록 주의","＜ 채용절차 ＞","[이런 고민을 하며 나아갑니다]","[ ML Research Team은 이런 팀입니다 ]","[합류 여정]","[근무지]","[핵클이 사용하는 기술]","[채용절차]","자주 묻는 질문"]
    }
}

# DB에서 URL 목록을 가져오기
s3_urls = get_s3_urls_from_db()

# Spark DataFrame으로 변환
s3_urls_df = spark.createDataFrame(s3_urls, ["id", "s3_text_url"])

# 섹션 추출을 위한 broadcast 변수
broadcast_sections = spark.sparkContext.broadcast(sections_to_extract)

# 각 URL에 대해 텍스트 파일을 읽고 섹션을 추출
def process_job_info(row):
    try:
        bucket_name, s3_key = extract_s3_details(row['s3_text_url'])
        job_description = get_s3_file_content(bucket_name, s3_key)

        # broadcast된 섹션 정보를 가져옵니다.
        sections = broadcast_sections.value
        
        key_tasks = extract_section(sections["주요업무"]["start_titles"], sections["주요업무"]["end_titles"], job_description)
        requirements = extract_section(sections["자격요건"]["start_titles"], sections["자격요건"]["end_titles"], job_description)
        preferred_qualifications = extract_section(sections["우대사항"]["start_titles"], sections["우대사항"]["end_titles"], job_description)

        # 처리된 정보를 리턴 (DB 업데이트를 위해)
        return (row['id'], key_tasks, requirements, preferred_qualifications)

    except Exception as e:
        print(f"Error processing URL {row['s3_text_url']}: {e}")
        return (row['id'], None, None, None)

# RDD로 변환 후 map 처리
processed_rdd = s3_urls_df.rdd.map(process_job_info)

# DB 업데이트는 batch 방식으로 처리
processed_rdd.foreachPartition(update_batch_to_db)

# Spark 세션 종료
spark.stop()

