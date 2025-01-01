import os
import pymysql
import boto3
from urllib.parse import urlparse
import pytesseract
from PIL import Image
import numpy as np
from io import BytesIO  # 추가: 이미지 데이터를 Bytes로 처리하기 위한 모듈

# RDS MySQL 접속 정보
host = "t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com"
user = "admin"  # RDS 생성 시 설정한 사용자 이름
password = "dltkddn1"  # 비밀번호
database = "testdb1"  # 사용하려는 데이터베이스 이름

# MySQL 서버에 연결
connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port=3306
)
cursor = connection.cursor()

# S3 클라이언트 설정
s3_client = boto3.client('s3')

# Tesseract 실행 경로 (Ubuntu에서는 기본적으로 /usr/bin/tesseract로 설치됩니다)
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# 파일 크기 제한 (예: 1KB = 1024 바이트)
max_file_size = 1 * 1024  # 1KB

# MySQL에서 s3_images_url이 NULL이 아닌 responsibility, qualification, preferential이 NULL인 레코드 조회
query = """
SELECT id, s3_images_url FROM combined_table WHERE s3_images_url IS NOT NULL AND (responsibility IS NULL AND qualification IS NULL AND preferential IS NULL)
"""
cursor.execute(query)
rows = cursor.fetchall()

# OCR 처리 함수
def perform_ocr(image_bytes):
    # PIL 이미지로 변환 (Tesseract는 PIL 이미지만 인식)
    pil_img = Image.open(BytesIO(image_bytes))

    # OCR 수행 (한글과 영어를 동시에 인식)
    custom_config = r'--oem 3 --psm 6'  # OCR 엔진 모드 (OEM)와 페이지 세그먼트 모드 (PSM) 설정
    text = pytesseract.image_to_string(pil_img, lang='kor+eng', config=custom_config)

    return text

# 이미지 다운로드 및 OCR 처리 후 MySQL에 저장
for row in rows:
    job_id = row[0]
    s3_urls = row[1]  # 쉼표로 구분된 URL 리스트
    
    # 먼저 중복된 notice_id가 있는지 확인
    check_query = "SELECT EXISTS(SELECT 1 FROM imagetotext WHERE notice_id = %s)"
    cursor.execute(check_query, (job_id,))
    exists = cursor.fetchone()[0]

    if exists:
        print(f"Job ID {job_id} already exists, skipping OCR and insertion.")
        continue  # 중복된 경우 해당 job_id는 건너뜀

    # 쉼표로 구분된 URL들을 분리
    s3_url_list = s3_urls.split(',')

    # 이미지와 LastModified 시간을 저장할 리스트
    images_and_times = []

    # 각 이미지 URL에 대해 파일 크기 및 등록 시간 계산
    for s3_url in s3_url_list:
        s3_url = s3_url.strip()  # 공백 제거

        # S3 URL에서 버킷 이름과 파일 경로 추출
        parsed_url = urlparse(s3_url)
        bucket_name = parsed_url.netloc.split('.')[0]
        file_key = parsed_url.path.lstrip('/')  # '/' 제거

        try:
            # 객체의 메타데이터를 가져와서 등록 시간 및 파일 크기 확인
            response = s3_client.head_object(Bucket=bucket_name, Key=file_key)
            last_modified = response['LastModified']
            file_size = response['ContentLength']

            # 파일 크기 출력
            print(f"Job ID {job_id}: Image URL {s3_url} - Size: {file_size} bytes")

            # 파일 크기가 1 KB 이하인 경우 건너뛰기
            if file_size <= max_file_size:
                print(f"Image for job_id {job_id} skipped due to small file size ({file_size} bytes).")
            else:
                # S3에서 파일을 메모리로 다운로드
                image_object = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                image_bytes = image_object['Body'].read()

                # 이미지 처리 및 OCR
                try:
                    ocr_result = perform_ocr(image_bytes)
                    
                    # OCR 결과가 공백이면 Null 처리
                    if not ocr_result.strip():  # OCR 결과가 공백일 경우
                        ocr_result = None
                    
                    # 이미지와 등록 시간을 리스트에 추가
                    images_and_times.append((last_modified, ocr_result))

                except Exception as e:
                    # OCR 처리 중 오류가 발생하면 해당 이미지를 건너뛰고 다음 이미지로 이동
                    print(f"Error processing image for job_id {job_id} at URL {s3_url}: {e}")
                    # OCR 실패한 경우 Null 처리
                    images_and_times.append((last_modified, None))
                    continue

        except s3_client.exceptions.ClientError as e:
            # 404 오류 처리
            if e.response['Error']['Code'] == '404':
                print(f"Error: Image for job_id {job_id} not found (404).")
            else:
                print(f"Error downloading image for job_id {job_id}: {e}")
        except Exception as e:
            print(f"Unexpected error for job_id {job_id}: {e}")

    # 등록 시간을 기준으로 내림차순 정렬 (가장 최신 시간이 먼저 오도록)
    images_and_times.sort(key=lambda x: x[0], reverse=True)  # 내림차순 정렬

    # 텍스트 추출 후 결합
    combined_text = ''
    for _, ocr_text in images_and_times:
        if ocr_text:
            combined_text += ocr_text + "\n"  # 각 이미지 텍스트를 줄바꿈으로 구분
        else:
            combined_text += "NULL\n"  # OCR 결과가 없으면 NULL을 추가

    # 중복된 notice_id가 없는 경우 삽입
    insert_query = """
    INSERT INTO imagetotext (notice_id, imgtotext)
    VALUES (%s, %s)
    """
    cursor.execute(insert_query, (job_id, combined_text))
    connection.commit()
    print(f"OCR result for job_id {job_id} inserted into the database.")

# 연결 종료
cursor.close()
connection.close()
