from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, lit
from pyspark.sql.types import StringType
import boto3
from datetime import datetime
import pymysql

# Spark 세션 생성
spark = SparkSession.builder \
    .appName("S3 Text Processing and MySQL Ingestion") \
    .getOrCreate()

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

def extract_text_from_s3_file(bucket_name, file_key):
    """S3에서 파일을 읽고 텍스트 추출"""
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return response['Body'].read().decode('utf-8')

def extract_sections(file_content, keyword_groups):
    """텍스트에서 섹션별 데이터 추출"""
    extracted_sections = {}
    for group in keyword_groups:
        section_name = group['section_name']
        start_keywords = group['start_keywords']
        end_keywords = group['end_keywords']
        
        start_index = None
        end_index = None
        section_text = ""
        
        for start in start_keywords:
            start_index = file_content.find(start)
            if start_index != -1:
                break
        
        if start_index != -1:
            for end in end_keywords:
                end_index = file_content.find(end, start_index)
                if end_index != -1:
                    break
        
        if start_index != -1 and end_index != -1:
            section_text = file_content[start_index:end_index].strip()
        
        extracted_sections[section_name] = section_text
    
    return extracted_sections

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

# S3 버킷 및 경로 지정
bucket_name = 't2jt'
prefix = 'job/DE/sources/jobkorea/txt/'  # S3에서 텍스트 파일이 있는 경로

# S3 파일 가져오기
files = list_s3_files(bucket_name, prefix)

# 텍스트 파일 데이터 로드
data = []
for file_key in files:
    if file_key.endswith('.txt'):
        file_content = extract_text_from_s3_file(bucket_name, file_key)
        sections = extract_sections(file_content, keyword_groups)
        data.append({
            "s3_text_url": f"s3://{bucket_name}/{file_key}",
            "responsibility": sections.get('주요업무', '')[:1000],
            "qualification": sections.get('자격요건', '')[:1000],
            "preferential": sections.get('우대사항', '')[:1000],
            "insert_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

# PySpark DataFrame 생성
df = spark.createDataFrame(data)

# MySQL 테이블에 적재
def save_to_mysql_partition(partition_data):
    """MySQL에 데이터 적재"""
    conn = pymysql.connect(
        host='43.201.40.223',
        user='user',
        password='1234',
        database='testdb',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    
    for row in partition_data:
        cursor.execute("""
            UPDATE jobkorea
            SET responsibility = %s, qualification = %s, preferential = %s, insert_time = %s
            WHERE s3_text_url = %s
            AND (responsibility IS NULL AND qualification IS NULL AND preferential IS NULL)
        """, (row['responsibility'], row['qualification'], row['preferential'], row['insert_time'], row['s3_text_url']))
    
    conn.commit()
    cursor.close()
    conn.close()

# PySpark RDD로 분산 처리 후 MySQL 적재
df.rdd.foreachPartition(save_to_mysql_partition)
