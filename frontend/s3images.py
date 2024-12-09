import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from io import BytesIO
from PIL import Image

# S3 설정
BUCKET_NAME = "t2jt"  # 사용 중인 S3 버킷 이름
BASE_PATH = "job/DE/sources/" 
# S3 클라이언트 설정
s3 = boto3.client("s3")

def list_directories():
    """
    S3 버킷에서 상위 디렉토리 목록을 가져옴
    """
    return [
        "rocketpunch/",
        "wanted/",
        "saramin/",
        "jobkorea/",
        "jumpit/",
        "incruit/",
    ]

def list_images(bucket_name, directory):
    """
    특정 디렉토리에서 이미지 파일 목록 가져오기
    """
    images = []
    continuation_token = None
    prefix = BASE_PATH + directory

    while True:
        if continuation_token:
            response = s3.list_objects_v2(
                Bucket=bucket_name, Prefix=prefix, ContinuationToken=continuation_token
            )
        else:
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        # 이미지 파일만 필터링
        images.extend(
            content["Key"]
            for content in response.get("Contents", [])
            if content["Key"].lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
        )

        # 다음 페이지가 있는 경우 ContinuationToken을 업데이트
        if response.get("IsTruncated"):  # 결과가 잘렸는지 확인
            continuation_token = response.get("NextContinuationToken")
        else:
            break

    return images

def load_image_from_s3(bucket_name, image_key):
    """
    S3에서 이미지를 읽어 PIL 이미지 객체로 반환
    """
    try:
        response = s3.get_object(Bucket=bucket_name, Key=image_key)
        img_data = response["Body"].read()
        return Image.open(BytesIO(img_data))
    except Exception as e:
        st.error(f"이미지를 로드하는 중 오류가 발생했습니다: {e}")
        return None

# Streamlit App
st.title("S3 디렉토리별 이미지 보기")

# S3 버킷에서 디렉토리 목록 가져오기
directories = list_directories()

if not directories:
    st.warning("버킷에 디렉토리가 없습니다.")
else:
    # 디렉토리 선택
    selected_directory = st.sidebar.selectbox("디렉토리를 선택하세요", directories)

    # 선택한 디렉토리의 이미지 목록 가져오기
    images = list_images(BUCKET_NAME, selected_directory)

    if not images:
        st.warning(f"{selected_directory} 디렉토리에 이미지가 없습니다.")
    else:
        # 이미지 목록을 페이지네이션으로 표시
        page = st.sidebar.number_input("페이지 번호", min_value=1, max_value=(len(images) - 1) // 5 + 1, value=1)
        start_idx = (page - 1) * 5
        end_idx = start_idx + 5

        # 선택한 페이지의 이미지 표시
        for image_key in images[start_idx:end_idx]:
            image = load_image_from_s3(BUCKET_NAME, image_key)
            if image:
                st.image(image, caption=image_key, use_container_width=True)
