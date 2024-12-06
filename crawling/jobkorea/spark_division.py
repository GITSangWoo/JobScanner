import re
import pymysql
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# SparkSession 초기화
spark = SparkSession.builder \
    .appName("JobInfoProcessing") \
    .getOrCreate()

# MySQL 연결 설정
def get_mysql_connection():
    return pymysql.connect(
        host='43.201.40.223',
        user='user',
        password='1234',
        database='testdb',
        port=3306
    )

# S3에서 텍스트 파일을 읽어오는 함수
def get_s3_file_content(bucket_name, s3_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=s3_key)
    file_content = response['Body'].read().decode('utf-8')
    return file_content

# S3 URL에서 버킷명과 객체 키 추출
def extract_s3_details(s3_url):
    url_parts = s3_url[5:].split('/', 1)
    bucket_name = url_parts[0]
    s3_key = url_parts[1]
    return bucket_name, s3_key

# 섹션 추출 함수
def extract_section(start_titles, end_titles, text):
    # 시작 키워드와 종료 키워드의 정규식 패턴 생성
    start_pattern = '|'.join([re.escape(start) for start in start_titles])
    end_pattern = '|'.join([re.escape(end) for end in end_titles])
    
    # 텍스트의 시작과 끝을 기준으로 섹션을 추출
    pattern = re.compile(rf"^(?:\s*)({start_pattern})(?:\s*)\n([\s\S]+?)(?=\n(?:\s*)({end_pattern})(?:\s*)|\Z)", re.MULTILINE)
    
    # 정규 표현식에 맞는 첫 번째 섹션을 찾기
    match = pattern.search(text)
    
    if match:
        # 섹션의 내용 반환 (앞뒤 공백 제거)
        return match.group(2).strip() 
    else:
        # 일치하는 섹션이 없으면 None 반환
        return None

# DB에서 URL 값 추출
def get_s3_urls_from_db():
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    query = """
        SELECT id, s3_text_url 
        FROM jobkorea
        WHERE 
            (responsibility IS NULL AND qualification IS NULL) OR
            (responsibility IS NULL AND preferential IS NULL) OR
            (qualification IS NULL AND preferential IS NULL)
        AND s3_text_url IS NOT NULL  -- None 값이 포함되지 않도록 추가
    """
    
    cursor.execute(query)
    urls = cursor.fetchall()
    connection.close()
    
    return urls

# DB 업데이트 함수 (Batch Insert 방식)
def update_batch_to_db(iterator):
    connection = get_mysql_connection()
    cursor = connection.cursor()
    
    batch_data = []
    for job_id, key_tasks, requirements, preferred_qualifications in iterator:
        batch_data.append((key_tasks, requirements, preferred_qualifications, job_id))

        # Batch 크기 조절
        if len(batch_data) >= 100:
            cursor.executemany("""
                UPDATE jobkorea 
                SET responsibility = %s, qualification = %s, preferential = %s 
                WHERE id = %s
            """, batch_data)
            connection.commit()
            batch_data = []

    if batch_data:
        cursor.executemany("""
            UPDATE jobkorea 
            SET responsibility = %s, qualification = %s, preferential = %s 
            WHERE id = %s
        """, batch_data)
        connection.commit()

    connection.close()

# 섹션 추출 설정
sections_to_extract = {
    "주요업무": {
        "start_titles": [
            "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "[담당업무] ", "이런 업무를 해요", "담당업무 내용",
            "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "# 담당업무 ",
            "  [우리는 이런일을 합니다]", "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]",
            "직무상세", "[ 업무 안내 ]", "업무 내용:", " 업무 내용 ", "직무소개", "업무 상세", ">> 이런 일을 합니다", "1) 주요업무", "이런 업무를 해요 (주요 업무)",
            "[ 담당업무 ]",
        ],
        "end_titles": [
            "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "자격 요건:", "필요역량 및 경험", "기술스택",
            "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 분들을 찾고 있어요", "필요역량 ", "  【기술스택】 이러한 툴을 활용해요",
            "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "# 자격요건", "[우리는 이런사람을 원합니다]", "  자격요건",
            "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", "[필수 기술]", "필수사항", "지원자격", "지원 자격", "지원자격 ","[ 필수(자격) 조건 ]", "경험/역량 ",
            "[필수 경험과 역량]", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ", "[우대사항] ", "[우대사항]",
            "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ", " 우대조건",
            "  【자격요건】 이러한 분을 찾고 있어요", "우대 사항:", "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 지원자격",
            "스킬", "모집 강의 주제 예시 (교안 및 교육 제공 / 일부만 강의 가능)", "개발 환경", "[모집절차]", "학력 및 경력", "기타 사항", " [ 근무 장소 ] ",
            "경력/기술 요건:", "우대사항 ", "[모집 절차]", "자격요건  ", "[Key Responsibilities]", "이런 조건에서 근무할 예정이에요", "청주본사",
            "[기본조건]", "기타사항", "[지원 및 진행 절차]", "  [자격 요건]", "[우대조건]", " 복리후생", "저희가 우대하는 분들은 :  ", "근무지",
            "●  요구 경험", "■ 근무시간", "자격사항", " [이런 경험이 있으시면 더욱 좋아요]", " [꼭 확인해 주세요!]", "□ 경력 요구사항", "□ 우대사항",
            "[경력] 경력 3년 이내", "[핵심역량 및 기술]", "기본자격", " [자격요건]", " [직무경험]", "전형절차", "근무 시간 및 장소", "자격조건",
            "지원 방법 및 채용 절차", "요구 사항", "우대 조건", "우대조건]", "[ Bigdata Engineer로 이런 분이 필요합니다 ]", ">> 이런 분을 찾습니다",
            ">> 이런 경험이 있다면 더욱 좋습니다", "2) 우대사항", "3) 자격요건", "이런 분들을 찾고 있어요 (자격 요건)", "이런 분이면 더 좋아요 (우대 사항)",
            "[자격요건] ", "○○명", "[ 공통 자격요건 ]", "[ 우대사항 ]",
        ]
    },
    "자격요건": {
        "start_titles": [
            "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "[우리는 이런사람을 원합니다]", "기술스택",
            "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 분들을 찾고 있어요", "# 자격요건", "자격 요건:", "필요역량 및 경험",
            "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "필요역량 ", "  【자격요건】 이러한 분을 찾고 있어요",
            "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", "[필수 기술]", "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량 ", "지원자격 ", "지원자격",
            "  자격요건", "[필수 경험과 역량]", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ", "자격요건  ", "[Key Responsibilities]",
            "[기본조건]", "  [자격 요건]", "●  요구 경험", "자격사항", "□ 경력 요구사항", "[핵심역량 및 기술]", "기본자격", " [자격요건]", "자격조건", "[자격요건] ",
            "[ Bigdata Engineer로 이런 분이 필요합니다 ]", ">> 이런 분을 찾습니다", "3) 자격요건", "이런 분들을 찾고 있어요 (자격 요건)", "모집부문 담당업무 자격요건 우대사항",
            "[ 공통 자격요건 ]",
        ],
        "end_titles": [
            "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "담당업무 내용", "  [우리는 이런일을 합니다]", "[담당업무] ",
            "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]","# 담당업무 ",
            "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", "[ 업무 안내 ]",
            "업무 내용:", " 업무 내용 ", "Project Manager", "[우대조건]", "저희가 우대하는 분들은 :  ", "이런 업무를 해요 (주요 업무)",
            "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ",
            "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:", "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건",
            "근무시작일", "스킬", "[급여 조건]", "Place of Work ", "[기타]", "[ 제출서류 ]", "직무상세", "전형 절차", "전형절차", "기타 사항", "기타사항",
            "드론(조종) 촬영 보조", "경력/기술 요건:", "우대사항 ", "환경안전", "필요역량", "[모집 절차]", "우대사항  ", "우대사항-", "[지원 및 진행 절차]",
            " 복리후생", "근무시간", "근무지", "3. 투입시기", "■ 근무시간", "수행업무", "( 15명 )"," [이런 경험이 있으시면 더욱 좋아요]", " [꼭 확인해 주세요!]",
            "□ 우대사항", "□ 직무상세", "[우대사항]", "우대 사항", "[우대조건]", "근무 시간 및 장소", "지원 방법 및 채용 절차", "업무 상세", "요구 사항",
            "우대 조건", "우대조건]", ">> 이런 일을 합니다", ">> 이런 경험이 있다면 더욱 좋습니다", "1) 주요업무", "2) 우대사항", "이런 분이면 더 좋아요 (우대 사항)",
            "근무형태 : 정규직 (수습기간 3개월)", "[우대사항] ", "○○명", "[ 담당업무 ]", "[ 우대사항 ]",
        ]
    },
    "우대사항": {
        "start_titles": [
            "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ", "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:",
            "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건", "우대사항 ", "우대사항-", "[우대조건]", "저희가 우대하는 분들은 :  ",
            " [이런 경험이 있으시면 더욱 좋아요]", "□ 우대사항", "[우대사항]", "요구 사항", "우대 조건", "우대조건]", "[ Bigdata Engineer로 이런 분을 우대합니다 ]",
            ">> 이런 경험이 있다면 더욱 좋습니다", "2) 우대사항", "이런 분이면 더 좋아요 (우대 사항)", "■ 우대사항", "[우대사항] ", "[ 우대사항 ]",
        ],
        "end_titles": [
            "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "# 담당업무 ", "담당업무 내용", "[담당업무] ",
            "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "  [우리는 이런일을 합니다]",
            "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", " 업무 내용 ",
            "직무상세", "[ 업무 안내 ]", "업무 내용:", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ",
            "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "필요역량 및 경험", "기술스택", "[필수 기술]",
            "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량", "지원자격 ", "  자격요건", "[필수 경험과 역량]", "자격요건  ",
            "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 기술이 필요해요", "[우리는 이런사람을 원합니다]", "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]",
            "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격요건] ", "[자격 요건]", "근무지", "# 자격요건","  【자격요건】 이러한 분을 찾고 있어요",
            "전형절차", "이런 조건에서 근무할 예정이에요", "○명", "근무조건", "스킬", "  【업무방향】 이러한 경험도 할 수 있어요", "혜택:", "혜택 및 복지", "기타사항",
            "제출서류", "▶ 지원서는 이렇게 작성하시면 좋아요", "[혜택 및 복지]", "지원자격", "측정", "기타 사항", "경력/기술 요건:", "●  요구 경험",
            "-----------------------------------------------------------------------", "[채용 전형 안내]", "BAT에 합류하는 여정", "기타 참고 사항", "Video Platform Team은 이런 팀입니다",
            "TSS > 기술컨설팅팀", "전형 절차 ", "전형 절차", "0명 ", "0명", "Full Stack Developer", "[모집 절차]", "[Key Responsibilities]", "[Application]",
            "○기타사항", "[근무 조건]", "[기본조건]", "기타사항 ㆍ사원~대리 직급 채용 희망", "[지원 및 진행 절차]", "  [자격 요건]", "재무팀 정규직", "지원 전 확인 부탁드립니다",
            "근무기간 : 6개월 (당사자 간 협의에 따라 연장 가능) / 인턴으로 3개월 근무 후 정규직 전환 평가", " 복리후생", "근무시간", "근무지", "■ 근무시간", "수행업무",
            "□ 기업문화 ", "자격사항", "근무조건 및 지원방법", " [꼭 확인해 주세요!]", "□ 경력 요구사항", "□ 직무상세", "[핵심역량 및 기술]","기본자격",
            " [자격요건]", " [직무경험]", "근무 시간 및 장소", "자격조건", "지원 방법 및 채용 절차", "업무 상세", ">> 이런 일을 합니다", ">> 이런 분을 찾습니다",
            "1) 주요업무", "3) 자격요건", "이런 업무를 해요 (주요 업무)", "이런 분들을 찾고 있어요 (자격 요건)", "___", "○○명", "[ 공통 자격요건 ]", "[ 담당업무 ]",
        ]
    }
}

# DB에서 URL 목록을 가져오기
s3_urls = get_s3_urls_from_db()

# Spark DataFrame으로 변환
s3_urls_df = spark.createDataFrame(s3_urls, ["id", "s3_text_url"])

# 섹션 추출을 위한 broadcast 변수
broadcast_sections = spark.sparkContext.broadcast(sections_to_extract)

# 각 URL에 대해 텍스트 파일을 읽고 섹션을 추출
def process_job_info(row):
    try:
        if row['s3_text_url'] is None:
            print(f"Skipping row with id {row['id']} because s3_text_url is None")
            return (row['id'], None, None, None)  # s3_text_url이 None일 경우 건너뛰기

        bucket_name, s3_key = extract_s3_details(row['s3_text_url'])
        job_description = get_s3_file_content(bucket_name, s3_key)

        # broadcast된 섹션 정보를 가져옵니다.
        sections = broadcast_sections.value
        
        key_tasks = extract_section(sections["주요업무"]["start_titles"], sections["주요업무"]["end_titles"], job_description)
        requirements = extract_section(sections["자격요건"]["start_titles"], sections["자격요건"]["end_titles"], job_description)
        preferred_qualifications = extract_section(sections["우대사항"]["start_titles"], sections["우대사항"]["end_titles"], job_description)

        return (row['id'], key_tasks, requirements, preferred_qualifications)

    except Exception as e:
        print(f"Error processing URL {row['s3_text_url']}: {e}")
        return (row['id'], None, None, None)


# 데이터프레임을 RDD로 변환하여 파티셔닝 처리
num_partitions = 3  # 3개의 파티션으로 분할
partitioned_rdd = s3_urls_df.rdd.repartition(num_partitions)

# 각 파티션에서 병렬로 DB 업데이트 처리
processed_rdd = partitioned_rdd.map(process_job_info)

# DB 업데이트는 batch 방식으로 처리
processed_rdd.foreachPartition(update_batch_to_db)

# Spark 세션 종료
spark.stop()