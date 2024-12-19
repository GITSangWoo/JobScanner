import pymysql
import json

#직업 정보 넣기

# MySQL 연결 설정
db_config = {
    'host': 't2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'dltkddn1',
    'database': 'service'
}

# JSON 파일 경로
json_file_path = './jobinfo.json'

def close_connection(cursor, conn):
    """연결과 커서를 안전하게 종료하는 함수"""
    if cursor:
        cursor.close()
    if conn:
        conn.close()
    print("DB 연결이 종료되었습니다.")

def insert_job_roles(json_file_path):
    """JSON 파일을 읽고 job_role 테이블에 데이터를 삽입하는 함수"""
    conn = None
    cursor = None

    try:
        # MySQL 연결
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # JSON 파일 읽기
        with open(json_file_path, 'r', encoding='utf-8') as file:
            job_role_data = json.load(file)

        # JSON 데이터를 SQL 삽입 쿼리로 변환
        for job in job_role_data:
            insert_query = """
                INSERT INTO job_role (job_title, role_name, role_description)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (job['job_title'], job['role_name'], job['role_description']))

        # 데이터 커밋 (변경 사항을 DB에 적용)
        conn.commit()
        print("데이터 삽입 완료!")

    except pymysql.MySQLError as err:
        print(f"MySQL Error: {err}")
    except FileNotFoundError:
        print(f"JSON 파일을 찾을 수 없습니다: {json_file_path}")
    except json.JSONDecodeError:
        print(f"JSON 파일을 읽을 수 없습니다: {json_file_path}")
    finally:
        # 연결 종료
        close_connection(cursor, conn)

# 삽입 작업 실행
insert_job_roles(json_file_path) 


