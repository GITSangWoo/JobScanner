from rocketpunch_crawling import get_job_posts
from rocketpunch_links import get_all_links
from s3_methods import get_yesterday_links, save_link_to_s3
from db_methods import update_deleted_links, update_content
from datetime import datetime as dt
from zoneinfo import ZoneInfo

# Variable declaration
kst = ZoneInfo("Asia/Seoul")

BUCKET_NAME = 't2jt'
S3_LINK_PATH = 'job/{abb}/airflow_test/rocketpunch/links/'
S3_TEXT_PATH = 'job/{abb}/airflow_test/rocketpunch/txt/'
S3_IMAGE_PATH = 'job/{abb}/airflow_test/rocketpunch/images/'  

# job_titles = {
#     "DE":"데이터 엔지니어", 
#     "DA":"데이터 분석가", 
#     "FE":"프론트엔드 엔지니어", 
#     "BE":"백엔드 엔지니어", 
#     "MLE":"머신러닝 엔지니어"
#     }
job_titles = {"DE":"데이터 엔지니어"}

def main():
    # 각 job_title 마다 url과 s3 directory assign 하기
    for job_abb, job_title in job_titles.items():

        # s3 링크 저장 경로 설정
        s3_link_path = S3_LINK_PATH.format(abb = job_abb)
        # s3안에 어제 링크 가지고 오기
        latest_links = get_yesterday_links(BUCKET_NAME, s3_link_path)
        # s3해당 디렉토리안에 txt없으면 오늘자 링크 수집으로 넘어가기 
        if latest_links is None:
            print(f"{s3_link_path}에 링크 txt 파일이 하나도 없으므로 오늘자 공고 링크 크롤링을 진행합니다...")
            latest_links = []
        else:
            print(f"[CHECKING] S3에서 받아온 최신 공고 리스트 길이: {len(latest_links)}")

        # 오늘자 링크 수집 진행
        today_links = get_all_links(job_title)
        print(f"[CHECKING] 오늘 크롤링한 최신 공고 리스트 길이: {len(today_links)}")
        today_date = dt.now(tz=kst).strftime('%Y%m%d')

        # 일단 오늘 수집한거 파일없이 메모리에서 바로 s3에 저장
        save_link_to_s3(BUCKET_NAME, s3_link_path, today_date, today_links)

        # 어제 리스트(latest_links) 와 오늘 리스트(today_links) 비교
        
        # 1. 제거된 공고 db에 removed time 업데이트 보내기
        links_removed = [link for link in latest_links if not today_links or link not in today_links]
        print(f"[CHECKING] 어제와 비교해 removed된 링크들: {len(links_removed)}개")
        update_deleted_links(links_removed)

        # 2. 추가된 공고에 대하여 rc 모듈사용 상세 공고 크롤링 진행 - 메타데이터 db로 바로
        links_added = [link for link in today_links if not latest_links or link not in latest_links]
        print(f"[CHECKING] 오늘 공고 크롤링을 진행할 링크의 개수: {len(links_added)}개")
        # links_added 크롤링 진행 - 하나 크롤링할때마다 바로 s3 전송
        s3_text_path = S3_TEXT_PATH.format(abb = job_abb) # s3 텍스트 저장 경로 설정
        s3_image_path = S3_IMAGE_PATH.format(abb = job_abb) # s3 이미지 저장 경로 설정

        """db넣는거 확인하면 오늘자 넣어서 2백 몇개 데이터 넣기, 아니면 맨 앞에 db데이터 없으면 링크 처음부터"""
        #job_posts = get_job_posts(BUCKET_NAME, today_links, s3_text_path, s3_image_path)
        job_posts = get_job_posts(BUCKET_NAME, links_added, job_title, s3_text_path, s3_image_path)
        print(f"[CHECKING] 오늘 크롤링한 공고의 개수: {len(job_posts)}개")
        # 그리고 저장된 path json으로 받아와서 db에 전부 업데이트 - dbmethods
        update_content(job_posts)

        print(f"🌟{job_title}에 대한 크롤링과 DB업데이트를 완료하였습니다!")
        
if __name__=="__main__":
    main()

# 추가로 고려해야할 사항 1. log어떻게