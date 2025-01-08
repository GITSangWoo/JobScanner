import pymysql
import json

# RDS 데이터베이스 연결 설정
db_config = {
    'host': 't2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com',
    'user': 'admin',
    'password': 'dltkddn1',
    'port': 3306
}

def close_connection(cursor, connection):
    """연결과 커서를 안전하게 종료하는 함수"""
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    print("DB 연결이 종료되었습니다.")

def filter_tot_tech(tot_tech_json):
    """tot_tech 값을 필터링하여 기술 목록을 반환하는 함수"""
    if tot_tech_json == '{}':
        return None  # 빈 JSON이므로 None을 반환하여 필터링된 기술 목록이 없도록 처리
    
    tech_dict = json.loads(tot_tech_json)  # JSON 문자열을 파이썬 딕셔너리로 변환
    tech_list = [key for key, value in tech_dict.items() if value == 1]  # 값이 1인 기술만 필터링
    return ', '.join(tech_list)  # 쉼표로 구분된 문자열로 반환

def insert_notice_data():
    """combined_table에서 데이터를 가져와 service의 notice 테이블에 삽입하는 함수"""
    connection = None
    cursor = None

    try:
        # testdb에 연결하여 데이터 가져오기
        connection = pymysql.connect(**db_config, database='testdb1')
        cursor = connection.cursor()

        # combined_table과 extract_tech_stack을 조인하는 쿼리 작성
        query = """
        SELECT 
            c.id,               -- combined_table의 id
            c.job_title,
            c.due_type,
            c.due_date,
            c.company,
            c.post_title,
            c.responsibility,
            c.qualification,
            c.preferential,
            e.tot_tech,
            c.org_url          -- org_url 추가
        FROM 
            combined_table c
        JOIN 
            extract_tech_stack e ON c.id = e.notice_id
        WHERE 
            c.removed_time IS NULL
            AND e.tot_tech != '{}'  -- tot_tech가 빈 JSON이 아닌 경우만 포함
        """

        # 쿼리 실행하여 데이터를 가져오기
        cursor.execute(query)
        rows = cursor.fetchall()

        # service 데이터베이스로 연결 변경
        connection.select_db('service')

        # 4. 가져온 데이터를 service 데이터베이스의 notice 테이블에 삽입
        insert_query = """
        INSERT INTO notice (
            notice_id,                 -- combined_table의 id
            due_date, 
            job_title, 
            due_type, 
            tot_tech, 
            company, 
            post_title, 
            preferential, 
            qualification, 
            responsibility,
            org_url                  -- org_url 추가
        ) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # 5. 한 행씩 service의 notice 테이블에 삽입
        for row in rows:
            # row 길이가 충분한지 확인하고, 인덱스 오류 방지
            if len(row) >= 11:  # 최소 11개의 컬럼이 있어야 한다고 가정 (id 포함)
                tot_tech = filter_tot_tech(row[9])  # tot_tech 값을 필터링하여 쉼표로 구분된 문자열로 변환
                org_url = row[10]  # org_url 값 가져오기

                try:
                    # 삽입 쿼리 실행
                    cursor.execute(insert_query, (
                        row[0],  # id
                        row[3],  # due_date
                        row[1],  # job_title
                        row[2],  # due_type
                        tot_tech, # tot_tech (필터링된 기술 목록)
                        row[4],  # company
                        row[5],  # post_title
                        row[8],  # preferential
                        row[7],  # qualification
                        row[6],  # responsibility
                        org_url   # org_url
                    ))
                except pymysql.MySQLError as e:
                    # 중복된 키 오류가 발생하면 해당 데이터를 건너뜁니다.
                    if e.args[0] == 1062:  # Duplicate entry 오류 코드
                        print(f"Skipping duplicate entry for notice_id {row[0]}")
                    else:
                        print(f"MySQL Error: {e}")
            
            else:
                print(f"Skipping row with insufficient columns: {row}")

        # 변경 사항 커밋
        connection.commit()
        print("데이터 삽입이 완료되었습니다.")

    except pymysql.MySQLError as err:
        print(f"MySQL Error: {err}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 연결 종료
        close_connection(cursor, connection)

# 삽입 작업 실행
insert_notice_data()

