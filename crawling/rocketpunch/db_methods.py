import pymysql
from datetime import datetime as dt
from zoneinfo import ZoneInfo

# 한국 시간대 설정
kst = ZoneInfo("Asia/Seoul")

# 삭제된 공고의 removed_time 업데이트 하는 함수
def update_deleted_links(links_removed):
    try:
        # MySQL 연결 설정
        connection = pymysql.connect(
            host='43.201.40.223',
            user='user',
            password='1234',
            database='testdb',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        current_time = dt.now(tz=kst).strftime('%Y-%m-%d %H:%M:%S')
        delete_time = dt.now(tz=kst).strftime('%Y-%m-%d')  # YYYYMMDD 형식

        with connection.cursor() as cursor:
            # 쿼리 템플릿
            query = """
                UPDATE airflowT
                SET 
                    update_time = %s,
                    removed_time = %s
                WHERE org_url = %s
            """
            count1 = 0
            count2 = 0
            # links_removed 리스트의 각 URL에 대해 업데이트 실행
            for url in links_removed:
                rows_affected = cursor.execute(query, (current_time, delete_time, url))
                if rows_affected == 0:
                    count1 += 1
                else:
                    count2 += 1
            print(f"DB에 반영된 레코드 수: {count2}, 반영되지 않은 레코드 수: {count1}")
            
            # 변경 사항 커밋
            connection.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if connection.open:
            connection.close()

def update_content(job_posts):
    """ 여러 job_post 딕셔너리를 rocketpunch 테이블에 삽입 또는 업데이트하는 함수."""
    try:
        connection = pymysql.connect(
            host='43.201.40.223',
            user='user',
            password='1234',
            database='testdb',
            port=3306,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        if not connection.open:
            print("❌ 데이터베이스 연결에 실패했습니다. 연결을 확인하세요.")
            return

        with connection.cursor() as cursor:
            print("✅ 데이터베이스 연결이 성공적으로 되었습니다.")
            query = """
                INSERT INTO airflowT (create_time, update_time, site, job_title, due_type, due_date, company, post_title, notice_type, org_url, s3_text_url, s3_images_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            for job_post in job_posts:
                try:
                    values = (
                        job_post.get('create_time'),
                        job_post.get('update_time'),
                        job_post.get('site'),
                        job_post.get('job_title'),
                        job_post.get('due_type'),
                        job_post.get('due_date'),
                        job_post.get('company'),
                        job_post.get('post_title'),
                        job_post.get('notice_type'),
                        job_post.get('org_url'),
                        job_post.get('s3_text_url'),
                        job_post.get('s3_images_url')
                    )
                    cursor.execute(query, values)
                    connection.commit()

                except Exception as e:
                    print(f"❌ 데이터 삽입 실패 (job_post: {job_post.get('org_url')}): {str(e)}")
                    connection.rollback()

            print("✅ 모든 데이터 삽입 및 업데이트가 성공했습니다!")

    except Exception as e:
        print(f"❌ 데이터베이스 작업 중 오류 발생: {e}")

    finally:
        if connection.open:
            connection.close()    
    




