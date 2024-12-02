import pymysql
from datetime import datetime as dt
from zoneinfo import ZoneInfo

# MySQL 연결 설정
connection = pymysql.connect(
    host='43.201.40.223',
    user='user',
    password='1234',
    database='testdb',
    port=3306,
    cursorclass=pymysql.cursors.DictCursor
)

# 한국 시간대 설정
kst = ZoneInfo("Asia/Seoul")

def unique_url():
    """ db의 org_url에 unique 특성 부여 (중복 방지)"""
    try:
        with connection.cursor() as cursor:
            query = """ 
                ALTER TABLE rocketpunch
                ADD CONSTRAINT unique_org_url UNIQUE (org_url);
            """
            # 쿼리 실행
            cursor.execute(query)

        # 트랜잭션 커밋
        connection.commit()
        print("✅ org_url column이 unique로 업데이트 되었습니다! ")
    except Exception as e:
        print(f"⛔ UNIQUE 제약 조건 추가 실패: {e}")
        # 트랜잭션 롤백
        connection.rollback()

# 삭제된 공고의 removed_time 업데이트 하는 함수
def update_deleted_links(links_removed):

    try:
        current_time = dt.now(tz=kst).strftime('%Y-%m-%d %H:%M:%S')
        delete_time = dt.now(tz=kst).strftime('%Y-%m-%d')  # YYYYMMDD 형식

        with connection.cursor() as cursor:
            # 쿼리 템플릿
            query = """
                UPDATE rocketpunch
                SET 
                    update_time = %s,
                    removed_time = %s
                WHERE org_url = %s
            """
            
            # links_removed 리스트의 각 URL에 대해 업데이트 실행
            for url in links_removed:
                rows_affected = cursor.execute(query, (current_time, delete_time, url))
                if rows_affected == 0:
                    print(f"No matching rows found for URL: {url}")
                else:
                    print(f"Updated delete_time and update_time for URL: {url}")
            
            # 변경 사항 커밋
            connection.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # 데이터베이스 연결 종료
        connection.close()

def update_content(job_posts):
    """ 여러 job_post 딕셔너리를 rocketpunch 테이블에 삽입 또는 업데이트하는 함수."""
    try:
        with connection.cursor() as cursor:
            # 삽입할 SQL 쿼리 작성 (ON DUPLICATE KEY UPDATE)
            query = """
                INSERT INTO rocketpunch (
                    create_time,
                    update_time,
                    removed_time,
                    site,
                    job_title,
                    due_type,
                    due_date,
                    company,
                    post_title,
                    notice_type,
                    org_url,
                    s3_text_url,
                    s3_images_url,
                    responsibility,
                    qualification,
                    preferential
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON DUPLICATE KEY UPDATE
                    update_time = VALUES(update_time),
                    removed_time = VALUES(removed_time),
                    due_type = VALUES(due_type),
                    due_date = VALUES(due_date),
                    company = VALUES(company),
                    post_title = VALUES(post_title),
                    notice_type = VALUES(notice_type),
                    s3_text_url = VALUES(s3_text_url),
                    s3_images_url = VALUES(s3_images_url),
                    responsibility = VALUES(responsibility),
                    qualification = VALUES(qualification),
                    preferential = VALUES(preferential)
            """

            # job_posts 리스트를 순회하면서 데이터를 삽입
            data_to_insert = []
            for job_post in job_posts:
                data_to_insert.append((
                    job_post.get('create_time'),
                    job_post.get('update_time'),
                    job_post.get('removed_time'),
                    job_post.get('site'),
                    job_post.get('job_title'),
                    job_post.get('due_type'),
                    job_post.get('due_date'),
                    job_post.get('company'),
                    job_post.get('post_title'),
                    job_post.get('notice_type'),
                    job_post.get('org_url'),
                    job_post.get('s3_text_url'),
                    job_post.get('s3_images_url'),
                    job_post.get('responsibility'),
                    job_post.get('qualification'),
                    job_post.get('preferential')
                ))

            # 데이터를 일괄 삽입 또는 업데이트
            cursor.executemany(query, data_to_insert)

        # 트랜잭션 커밋
        connection.commit()
        print("✅ 데이터 삽입 및 업데이트가 성공했습니다!")
    except Exception as e:
        print(f"❌ 데이터 삽입 또는 업데이트 실패: {e}")
        # 트랜잭션 롤백
        connection.rollback()

    finally:
        # 연결 닫기 (연결을 유지하는 것이 아니라면)
        cursor.close()



