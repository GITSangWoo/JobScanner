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

# rank_history 테이블 생성 함수
def create_rank_history_table_if_not_exists(connection):
    try:
        with connection.cursor() as cursor:
            # rank_history 테이블 존재 여부 확인 및 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rank_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    ranked_date DATE,
                    category VARCHAR(20),
                    job_title VARCHAR(4),
                    rank1 VARCHAR(30),
                    rank2 VARCHAR(30),
                    rank3 VARCHAR(30),
                    rank4 VARCHAR(30),
                    rank5 VARCHAR(30),
                    rank6 VARCHAR(30),
                    rank7 VARCHAR(30),
                    rank8 VARCHAR(30),
                    rank9 VARCHAR(30),
                    rank10 VARCHAR(30)
                );
            """)
            connection.commit()
    except Exception as e:
        print(f"Error creating table: {e}")
        connection.rollback()

# 기술 스택에서 상위 10개를 추출하는 함수 (카운팅 값이 0인 경우 제외)
def get_top_10_skills(skill_data):
    # 기술 스택 데이터를 내림차순(카운팅 값) + 알파벳 오름차순으로 정렬
    sorted_skills = sorted(skill_data.items(), key=lambda x: (-x[1], x[0]))
    
    # 카운팅 값이 0인 경우 제외하고 상위 10개의 기술 이름만 추출
    top_10_skills = [skill[0] if skill[1] > 0 else None for skill in sorted_skills[:10]]
    
    # 부족한 순위를 NULL로 채움
    while len(top_10_skills) < 10:
        top_10_skills.append(None)
    
    return top_10_skills

# agg_tech_stack 데이터를 rank_history 테이블로 전처리 및 삽입
def process_and_insert_data():
    connection = connect_to_db()
    try:
        # 테이블 생성 여부 확인 및 생성
        create_rank_history_table_if_not_exists(connection)

        with connection.cursor() as cursor:
            # agg_tech_stack 테이블 데이터 가져오기
            cursor.execute("SELECT agg_date, tot_agg, res_agg, qual_agg, pref_agg FROM agg_tech_stack")
            agg_data = cursor.fetchall()

            for row in agg_data:
                agg_date = row["agg_date"]
                categories = {
                    "total": json.loads(row["tot_agg"]),
                    "responsibility": json.loads(row["res_agg"]),
                    "qualification": json.loads(row["qual_agg"]),
                    "preferential": json.loads(row["pref_agg"])
                }

                for category_name, category_data in categories.items():
                    for job_title, skill_counts in category_data.items():
                        # 상위 10개의 기술 추출 (카운팅 값이 0인 경우 NULL 처리)
                        top_skills = get_top_10_skills(skill_counts)

                        # rank_history 테이블에 데이터 삽입
                        cursor.execute("""
                            INSERT INTO rank_history (
                                ranked_date, category, job_title,
                                rank1, rank2, rank3, rank4, rank5,
                                rank6, rank7, rank8, rank9, rank10
                            ) VALUES (
                                %s, %s, %s,
                                %s, %s, %s, %s, %s,
                                %s, %s, %s, %s, %s
                            )
                        """, (
                            agg_date, category_name, job_title,
                            *top_skills  # unpack top 10 skills into the query
                        ))

            # 변경사항 커밋
            connection.commit()

    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == "__main__":
    process_and_insert_data()
