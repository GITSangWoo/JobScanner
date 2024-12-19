import pymysql
import json
from collections import defaultdict
from datetime import datetime

# 직군별 기술 집계 


# RDS MySQL 접속 정보
mysql_host = "t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com"
mysql_user = "admin"  # RDS 생성 시 설정한 사용자 이름
mysql_password = "dltkddn1"  # 비밀번호
mysql_db = "testdb"  # 사용하려는 데이터베이스 이름

# MySQL에서 combined_table과 extract_tech_stack 테이블을 결합하여 데이터를 가져오는 함수
def fetch_combined_and_tech_stack_data():
    connection = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db,
        charset='utf8mb4'
    )
    try:
        with connection.cursor() as cursor:
            # combined_table과 extract_tech_stack을 결합하여 notice_id와 기술 스택 데이터를 가져오는 쿼리
            cursor.execute("""
                SELECT c.job_title, es.tot_tech, es.res_tech, es.qual_tech, es.pref_tech
                FROM extract_tech_stack es
                JOIN combined_table c ON es.notice_id = c.id
                WHERE c.removed_time IS NULL
            """)
            rows = cursor.fetchall()
            return rows
    finally:
        connection.close()

# MySQL에 집계된 기술 스택 저장 (agg_tech_stack 테이블)
def save_agg_to_db(agg_date, tot_agg, res_agg, qual_agg, pref_agg):
    connection = pymysql.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_db,
        charset='utf8mb4'
    )
    try:
        with connection.cursor() as cursor:
            # 해당 날짜에 데이터가 존재하면 업데이트, 없으면 삽입
            query = """
                INSERT INTO agg_tech_stack (agg_date, tot_agg, res_agg, qual_agg, pref_agg)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    tot_agg = VALUES(tot_agg),
                    res_agg = VALUES(res_agg),
                    qual_agg = VALUES(qual_agg),
                    pref_agg = VALUES(pref_agg)
            """
            cursor.execute(query, (agg_date, json.dumps(tot_agg), json.dumps(res_agg), json.dumps(qual_agg), json.dumps(pref_agg)))
            connection.commit()
    finally:
        connection.close()

# 기술 스택을 직군별로 집계하는 함수
def aggregate_tech_stacks(rows):
    # 직군별로 기술 스택을 집계할 딕셔너리 준비
    tot_agg = defaultdict(lambda: defaultdict(int))
    res_agg = defaultdict(lambda: defaultdict(int))
    qual_agg = defaultdict(lambda: defaultdict(int))
    pref_agg = defaultdict(lambda: defaultdict(int))

    for row in rows:
        job_title = row[0]  # job_title 값을 추출
        tot_tech = json.loads(row[1]) if row[1] else {}
        res_tech = json.loads(row[2]) if row[2] else {}
        qual_tech = json.loads(row[3]) if row[3] else {}
        pref_tech = json.loads(row[4]) if row[4] else {}

        # 각 직군(job_title)별로 기술 스택 합산
        for tech, value in tot_tech.items():
            tot_agg[job_title][tech] += value
        for tech, value in res_tech.items():
            res_agg[job_title][tech] += value
        for tech, value in qual_tech.items():
            qual_agg[job_title][tech] += value
        for tech, value in pref_tech.items():
            pref_agg[job_title][tech] += value

    return tot_agg, res_agg, qual_agg, pref_agg

# 메인 실행 부분
# 데이터를 가져옵니다
rows = fetch_combined_and_tech_stack_data()

if not rows:
    print("No data found to aggregate.")
else:
    # 기술 스택 직군별 집계
    tot_agg, res_agg, qual_agg, pref_agg = aggregate_tech_stacks(rows)

    # 오늘 날짜를 가져옵니다
    agg_date = datetime.now().date()

    # 집계된 데이터를 agg_tech_stack 테이블에 저장
    save_agg_to_db(agg_date, tot_agg, res_agg, qual_agg, pref_agg)
    print(f"Aggregated data for {agg_date} saved to agg_tech_stack.")

