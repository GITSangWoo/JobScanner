import os
import pymysql
import boto3
from urllib.parse import urlparse

# MySQL 연결 설정
connection = pymysql.connect(
    host='43.201.40.223',
    user='user',
    password='1234',
    database='testdb',
    port=3306
)
cursor = connection.cursor()

# S3 클라이언트 설정
s3_client = boto3.client('s3')

# 로컬 저장 폴더 설정
image_dir = "keyimages"
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# 파일 크기 제한 (예: 1KB = 1024 바이트)
max_file_size = 1 * 1024  # 1KB

# MySQL에서 s3_images_url이 NULL이 아닌 레코드 조회
query = """
SELECT id, s3_images_url FROM jobkorea WHERE s3_images_url IS NOT NULL
"""
cursor.execute(query)
rows = cursor.fetchall()

# 각 행에 대해 S3에서 이미지 다운로드
for row in rows:
    job_id = row[0]
    s3_urls = row[1]  # 쉼표로 구분된 URL 리스트
    
    # 쉼표로 구분된 URL들을 분리
    s3_url_list = s3_urls.split(',')

    for s3_url in s3_url_list:
        s3_url = s3_url.strip()  # 공백 제거

        # S3 URL에서 버킷 이름과 파일 경로 추출
        parsed_url = urlparse(s3_url)
        bucket_name = parsed_url.netloc.split('.')[0]
        file_key = parsed_url.path.lstrip('/')  # '/' 제거

        try:
            # 객체의 메타데이터를 가져와서 파일 크기 확인
            response = s3_client.head_object(Bucket=bucket_name, Key=file_key)
            file_size = response['ContentLength']
            
            # 파일 크기가 1 KB 이하인 경우 건너뛰기
            if file_size <= max_file_size:
                print(f"Image for job_id {job_id} skipped due to small file size ({file_size} bytes).")
            else:
                # S3에서 파일 다운로드
                s3_client.download_file(bucket_name, file_key, os.path.join(image_dir, f"{job_id}_{os.path.basename(file_key)}"))
                print(f"Image for job_id {job_id} downloaded successfully.")
        except s3_client.exceptions.ClientError as e:
            # 404 오류 처리
            if e.response['Error']['Code'] == '404':
                print(f"Error: Image for job_id {job_id} not found (404).")
            else:
                print(f"Error downloading image for job_id {job_id}: {e}")
        except Exception as e:
            print(f"Unexpected error for job_id {job_id}: {e}")

# 연결 종료
cursor.close()
connection.close()