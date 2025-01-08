import pymysql
import json

# MySQL RDS 접속 정보
DB_HOST = "t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com"
DB_PORT = 3306
DB_USER = "admin"
DB_PASSWORD = "dltkddn1"
DB_NAME = "testdb1"

# 데이터베이스 연결 함수
def connect_to_db():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# rank_count 테이블 생성 함수
def create_rank_count_table_if_not_exists(connection):
    try:
        with connection.cursor() as cursor:
            # rank_count 테이블 존재 여부 확인 및 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rank_count (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    history_id INT,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    rank1count INT,
                    rank2count INT,
                    rank3count INT,
                    rank4count INT,
                    rank5count INT,
                    rank6count INT,
                    rank7count INT,
                    rank8count INT,
                    rank9count INT,
                    rank10count INT,
                    FOREIGN KEY (history_id) REFERENCES rank_history(id) ON DELETE CASCADE
                );
            """)
            connection.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
        connection.rollback()

# rank_count 테이블에 데이터 삽입
def insert_rank_count():
    connection = connect_to_db()
    try:
        # 테이블 생성 여부 확인 및 생성
        create_rank_count_table_if_not_exists(connection)

        with connection.cursor() as cursor:
            # rank_history 테이블에서 데이터 가져오기
            cursor.execute("SELECT * FROM rank_history")
            rank_history_data = cursor.fetchall()

            for history_row in rank_history_data:
                history_id = history_row["id"]
                ranked_date = history_row["ranked_date"]
                category = history_row["category"]
                job_title = history_row["job_title"]

                # rank1 ~ rank10 기술 이름 가져오기
                ranks = [
                    history_row[f"rank{i}"] for i in range(1, 11)
                ]

                # agg_tech_stack에서 해당 날짜와 카테고리, 직군 데이터를 가져오기
                cursor.execute("""
                    SELECT tot_agg, res_agg, qual_agg, pref_agg 
                    FROM agg_tech_stack 
                    WHERE agg_date = %s
                """, (ranked_date,))
                agg_data = cursor.fetchone()

                if not agg_data:
                    print(f"No agg_tech_stack data found for date {ranked_date}")
                    continue

                # 카테고리에 따라 적절한 컬럼 선택 및 JSON 파싱
                category_column_map = {
                    "total": "tot_agg",
                    "responsibility": "res_agg",
                    "qualification": "qual_agg",
                    "preferential": "pref_agg"
                }
                selected_column = category_column_map.get(category)
                if not selected_column:
                    print(f"Unknown category: {category}")
                    continue

                skill_counts_json = json.loads(agg_data[selected_column])
                job_skill_counts = skill_counts_json.get(job_title, {})

                # 각 rank별 기술의 카운팅 값 가져오기
                rank_counts = [job_skill_counts.get(rank, 0) for rank in ranks]

                # rank_count 테이블에 데이터 삽입
                cursor.execute("""
                    INSERT INTO rank_count (
                        history_id, 
                        create_time, update_time,
                        rank1count, rank2count, rank3count, 
                        rank4count, rank5count, rank6count,
                        rank7count, rank8count, rank9count, 
                        rank10count
                    ) VALUES (
                        %s, NOW(), NOW(),
                        %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s,
                        %s
                    )
                """, (
                    history_id,
                    *rank_counts  # unpacking the counts for each rank
                ))

            # 변경사항 커밋
            connection.commit()

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    insert_rank_count()
