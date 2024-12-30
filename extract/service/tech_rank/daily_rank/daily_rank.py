import mysql.connector

# MySQL 연결: testdb 데이터베이스에서 rank_history와 rank_count 데이터를 조회
conn_testdb = mysql.connector.connect(
    host="t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com",
    user="admin",
    password="dltkddn1",
    database="testdb"
)
cursor_testdb = conn_testdb.cursor()

# MySQL 연결: service 데이터베이스에 daily_rank 데이터 삽입
conn_service = mysql.connector.connect(
    host="t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com",
    user="admin",
    password="dltkddn1",
    database="service"
)
cursor_service = conn_service.cursor()

# daily_rank 테이블 초기화
cursor_service.execute("TRUNCATE TABLE daily_rank")

# testdb의 rank_history 테이블에서 필요한 데이터 조회
cursor_testdb.execute("SELECT id, job_title, category, rank1, rank2, rank3, rank4, rank5, rank6, rank7, rank8, rank9, rank10 FROM rank_history")
rank_history_data = cursor_testdb.fetchall()

# testdb의 rank_count 테이블에서 필요한 데이터 조회
cursor_testdb.execute("SELECT history_id, rank1count, rank2count, rank3count, rank4count, rank5count, rank6count, rank7count, rank8count, rank9count, rank10count FROM rank_count")
rank_count_data = cursor_testdb.fetchall()

# rank_history와 rank_count에서 가져온 데이터를 service 데이터베이스의 daily_rank 테이블에 삽입
for history_row, count_row in zip(rank_history_data, rank_count_data):
    history_id, job_title, category, *ranks = history_row
    count_values = count_row[1:]  # rank1count, rank2count, ..., rank10count

    # tech_name이 tech_stack 테이블에 있는지 확인하고 없는 경우 건너뛰기
    for i in range(10):  # rank1부터 rank10까지 반복
        tech_name = ranks[i]
        
        if not tech_name:  # tech_name이 None 또는 빈 문자열일 경우 건너뛰기
            continue
        
        # tech_stack 테이블에서 tech_name이 존재하는지 확인
        cursor_service.execute("SELECT COUNT(*) FROM tech_stack WHERE tech_name = %s", (tech_name,))
        result = cursor_service.fetchone()
        
        if result[0] == 0:  # tech_name이 존재하지 않으면 건너뛰기
            print(f"{tech_name} is not in tech_stack, skipping...")
            continue  # tech_stack에 존재하지 않으면 건너뛰기
        
        # daily_rank 테이블에 데이터 삽입
        count = count_values[i]
        query = """
            INSERT INTO daily_rank (tech_name, job_title, category, count)
            VALUES (%s, %s, %s, %s)
        """
        cursor_service.execute(query, (tech_name, job_title, category, count))
        print(f"Inserted {tech_name} into daily_rank")

# 변경 사항 커밋
conn_service.commit()

# 연결 종료
cursor_testdb.close()
conn_testdb.close()
cursor_service.close()
conn_service.close()
