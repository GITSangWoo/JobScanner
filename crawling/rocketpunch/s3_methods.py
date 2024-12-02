import boto3
import requests
import time
import uuid

def get_yesterday_links(bucket_name, s3_link_path, max_retries=3, retry_delay=2):
    """ s3에서 링크 txt 최신것 읽어와서 리스트로 저장, 없으면 pass하고 링크 크롤링"""
    # S3 클라이언트 생성, 특정 클라이언트(다른 계정)을 경우에는 세션을 먼저 설정
    s3 = boto3.client('s3')
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=s3_link_path)

        # S3 links 디렉토리에 파일이 아예 없을 경우 처리
        if 'Contents' not in response:
            print(f"No files found in S3 path: {s3_link_path}")
            return None
        
        # txt 파일만 필터링
        txt_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.txt')]
        
        # 가장 최근 날짜의 파일 찾기
        latest_file = max(txt_files, key=lambda x: x['LastModified'])
        latest_file_key = latest_file['Key']

        # 파일 내용 읽기 (재시도 로직 포함)
        for attempt in range(max_retries):
            try:
                obj = s3.get_object(Bucket=bucket_name, Key=latest_file_key)
                file_content = obj['Body'].read().decode('utf-8')
                print(f"S3에서 찾은 최신 공고링크 파일: {latest_file_key}")

                # "url1\nurl2\nurl3" 형식으로 나오므로 list로 변환
                url_list = file_content.splitlines()
                return url_list
            
            # 접속 장애 에러 핸들링
            except Exception as e:
                print(f"Error reading file {latest_file_key}. Retrying {attempt + 1}/{max_retries}...")
                time.sleep(retry_delay)
        
        # 모든 재시도 실패 시
        print(f"Failed to read file {latest_file_key} after {max_retries} attempts.")
        return None

    except Exception as e:
        print(f"Error while accessing S3 to get yesterday job post links list: {e}")
        return None

def save_link_to_s3(bucket_name, s3_link_path, today_date, today_links):
    """ S3 버킷에 파일을 업로드합니다.
    
    :param file_name: 업로드할 파일
    :param bucket: 업로드될 버킷
    :param object_name: S3 객체이름. 없으면 file_name 사용
    :return: 파일이 업로드되면 True, 아니면 False
    """
    # S3 클라이언트 생성, 특정 클라이언트(다른 계정)을 경우에는 세션을 먼저 설정
    s3 = boto3.client('s3')
    file_content = "\n".join(today_links)
    list_key = f"{s3_link_path}{today_date}.txt"
    # S3에 파일 업로드
    try:
        s3.put_object(Bucket=bucket_name, Key=list_key, Body=file_content)
        print(f"File successfully uploaded to S3 at {list_key}")
        return True
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        return False
    
def upload_text_to_s3(bucket_name, s3_text_path, texts):
    """
    텍스트를 S3에 업로드하고 URL을 반환하는 함수
    """
    s3 = boto3.client('s3')
    text_uuid = str(uuid.uuid4())  # UUID 생성
    text_key = f"{s3_text_path}{text_uuid}.txt"  # S3에 저장할 경로 및 파일명
    try:
        s3.put_object(Bucket=bucket_name, Key=text_key, Body=texts)
        text_url = f"s3://{bucket_name}/{text_key}"
        return text_url
    except Exception as e:
        print(f"Failed to upload text to S3: {e}")
        return None

def upload_image_to_s3(bucket_name, s3_image_path, image_urls):
    """
    이미지 URL 리스트를 받아 이미지를 S3에 업로드하고 S3 URL 리스트를 반환하는 함수
    """
    s3 = boto3.client('s3')
    s3_urls = []  # 업로드된 S3 URL을 저장할 리스트

    for image_url in image_urls:
        try:
            # 이미지 다운로드
            response = requests.get(image_url, stream=True)
            response.raise_for_status()  # 다운로드 오류 시 예외 발생

            # UUID로 고유 이름 생성
            image_uuid = str(uuid.uuid4())
            image_key = f"{s3_image_path}/{image_uuid}.jpg"

            # S3에 업로드
            s3.upload_fileobj(response.raw, bucket_name, image_key)

            # 업로드된 S3 URL 생성
            s3_url = f"s3://{bucket_name}/{image_key}"
            s3_urls.append(s3_url)

        except Exception as e:
            print(f"이미지 업로드 실패 ({image_url}): {e}")

    # 콤마로 연결된 S3 URL 반환
    return s3_urls

