import boto3
import mysql.connector
from mysql.connector import pooling
import datetime
import re
import pymysql
from datetime import datetime
import os
import time

# 컨테이너 작업 디렉토리 변경
os.chdir("/code/plugins")


def jumpit_txt():
    # S3 클라이언트 설정
    s3_client = boto3.client('s3')

    # S3 버킷에서 지정된 prefix(경로)에 있는 모든 파일 목록을 반환
    def list_s3_files(bucket_name, prefix):
        files = []
        continuation_token = None
        while True:
            params = {
                'Bucket': bucket_name,
                'Prefix': prefix
            }
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            
            response = s3_client.list_objects_v2(**params)
            files.extend([content['Key'] for content in response.get('Contents', [])])
            continuation_token = response.get('NextContinuationToken')
            if not continuation_token:
                break
        return files

    # S3에서 파일을 읽고 텍스트 추출
    def extract_text_from_s3_file(bucket_name, file_key, keyword_groups):
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        
        extracted_sections = {}
        for group in keyword_groups:
            section_name = group['section_name']
            start_keywords = group['start_keywords']
            end_keywords = group['end_keywords']
            
            start_index = None
            end_index = None
            section_text = ""
            
            for start in start_keywords:
                start_index = file_content.find(start)
                if start_index != -1:
                    break
            
            if start_index != -1:
                for end in end_keywords:
                    end_index = file_content.find(end, start_index)
                    if end_index != -1:
                        break
            
            if start_index != -1 and end_index != -1:
                section_text = file_content[start_index:end_index].strip()
            
            extracted_sections[section_name] = section_text
        
        return extracted_sections

    # S3 데이터를 처리하고 MySQL에 적재
    def process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn):
        # S3 버킷에서 텍스트 파일 목록 가져오기
        files = list_s3_files(bucket_name, prefix)
        cursor = conn.cursor()
    
    # max_length = 1000  # 최대 길이 설정

        for file_key in files:
            if file_key.endswith('.txt'):  # .txt 파일만 처리
                sections = extract_text_from_s3_file(bucket_name, file_key, keyword_groups)
                full_s3_url = "s3://t2jt/" + file_key  # S3 파일 URL 생성
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시각
                
                # 텍스트 길이 제한
                responsibility = sections.get('주요업무', '')
                qualification = sections.get('자격요건', '')
                preferential = sections.get('우대사항', '')
                
                # MySQL 데이터 삽입/업데이트
                cursor.execute("""
                    UPDATE jumpit
                    SET update_time = %s, responsibility = %s, qualification = %s, preferential = %s
                    WHERE s3_text_url = %s
                    AND (responsibility IS NULL AND qualification IS NULL AND preferential IS NULL)
                """, (current_time, responsibility, qualification, preferential, full_s3_url))
        
        conn.commit()
        cursor.close()

    # 키워드 그룹 정의
    keyword_groups = [
        {
            "section_name": "주요업무",
            "start_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "[담당업무] ", "이런 업무를 해요", "담당업무 내용",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "# 담당업무 ",
                "  [우리는 이런일을 합니다]", "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", " 업무 내용 ", "직무소개",
            ],
            "end_keywords": [
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
                "[경력] 경력 3년 이내", "[핵심역량 및 기술]",
            ]
        },
        {
            "section_name": "자격요건",
            "start_keywords": [
                "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "[우리는 이런사람을 원합니다]", "기술스택",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 분들을 찾고 있어요", "# 자격요건", "자격 요건:", "필요역량 및 경험",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "필요역량 ", "  【자격요건】 이러한 분을 찾고 있어요",
                "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", "[필수 기술]", "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량 ", "지원자격 ", "지원자격",
                "  자격요건", "[필수 경험과 역량]", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ", "자격요건  ", "[Key Responsibilities]",
                "[기본조건]", "  [자격 요건]", "●  요구 경험", "자격사항", "□ 경력 요구사항", "[핵심역량 및 기술]",
            ],
            "end_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "담당업무 내용", "  [우리는 이런일을 합니다]", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]","# 담당업무 ",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", "[ 업무 안내 ]",
                "업무 내용:", " 업무 내용 ", "Project Manager", "[우대조건]", "저희가 우대하는 분들은 :  ",
                "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ",
                "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:", "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건",
                "근무시작일", "스킬", "[급여 조건]", "Place of Work ", "[기타]", "[ 제출서류 ]", "직무상세", "전형 절차", "전형절차", "기타 사항", "기타사항",
                "드론(조종) 촬영 보조", "경력/기술 요건:", "우대사항 ", "환경안전", "필요역량", "[모집 절차]", "우대사항  ", "우대사항-", "[지원 및 진행 절차]",
                " 복리후생", "근무시간", "근무지", "3. 투입시기", "■ 근무시간", "수행업무", "( 15명 )"," [이런 경험이 있으시면 더욱 좋아요]", " [꼭 확인해 주세요!]",
                "□ 우대사항", "□ 직무상세", "[우대사항]", "우대 사항",
            ]
        },
        {
            "section_name": "우대사항",
            "start_keywords": [
                "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ", "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:",
                "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건", "우대사항 ", "우대사항-", "[우대조건]", "저희가 우대하는 분들은 :  ",
                " [이런 경험이 있으시면 더욱 좋아요]", "□ 우대사항", "[우대사항]",
            ],
            "end_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "# 담당업무 ", "담당업무 내용", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "  [우리는 이런일을 합니다]",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", " 업무 내용 ",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ",
                "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "필요역량 및 경험", "기술스택", "[필수 기술]",
                "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량", "지원자격 ", "  자격요건", "[필수 경험과 역량]", "자격요건  ",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 기술이 필요해요", "[우리는 이런사람을 원합니다]", "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "근무지", "# 자격요건","  【자격요건】 이러한 분을 찾고 있어요",
                "전형절차", "이런 조건에서 근무할 예정이에요", "○명", "근무조건", "스킬", "  【업무방향】 이러한 경험도 할 수 있어요", "혜택:", "혜택 및 복지", "기타사항",
                "제출서류", "▶ 지원서는 이렇게 작성하시면 좋아요", "[혜택 및 복지]", "지원자격", "측정", "기타 사항", "경력/기술 요건:", "●  요구 경험",
                "-----------------------------------------------------------------------", "[채용 전형 안내]", "BAT에 합류하는 여정", "기타 참고 사항", "Video Platform Team은 이런 팀입니다",
                "TSS > 기술컨설팅팀", "전형 절차 ", "전형 절차", "0명 ", "0명", "Full Stack Developer", "[모집 절차]", "[Key Responsibilities]", "[Application]",
                "○기타사항", "[근무 조건]", "[기본조건]", "기타사항 ㆍ사원~대리 직급 채용 희망", "[지원 및 진행 절차]", "  [자격 요건]", "재무팀 정규직", "지원 전 확인 부탁드립니다",
                "근무기간 : 6개월 (당사자 간 협의에 따라 연장 가능) / 인턴으로 3개월 근무 후 정규직 전환 평가", " 복리후생", "근무시간", "근무지", "■ 근무시간", "수행업무",
                "□ 기업문화 ", "자격사항", "근무조건 및 지원방법", " [꼭 확인해 주세요!]", "□ 경력 요구사항", "□ 직무상세", "[핵심역량 및 기술]",
            ]
        }
    ]

    # MySQL 연결 설정
    conn = pymysql.connect(
        host='43.201.40.223',          # AWS 퍼블릭 IP
        user='user',                   # MySQL 사용자
        password='1234',               # MySQL 비밀번호
        database='testdb',             # 데이터베이스 이름
        charset='utf8mb4'
    )

    # S3 버킷과 경로 지정
    bucket_name = 't2jt'
    prefix = 'job/DE/sources/jumpit/txt/'  # S3에서 텍스트 파일이 있는 경로

    # 데이터 처리 및 MySQL로 바로 적재
    process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn)

    # MySQL 연결 종료
    conn.close()

def wanted_txt():
    # MySQL 연결 설정
    connection = pymysql.connect(
        host='43.201.40.223',
        user='user',
        password='1234',
        database='testdb',
        port=3306
    )

    # S3에서 텍스트 파일을 읽어오는 함수
    def get_s3_file_content(bucket_name, s3_key):
        try:
            s3 = boto3.client('s3')
            response = s3.get_object(Bucket=bucket_name, Key=s3_key)
            file_content = response['Body'].read().decode('utf-8')
            return file_content
        except Exception as e:
            print(f"Error fetching S3 file {s3_key}: {e}")
            return ""

    # S3 URL에서 버킷명과 객체 키 추출
    def extract_s3_details(s3_url):
        url_parts = s3_url[5:].split('/', 1)  # 's3://' 부분을 제거하고, 첫 번째 '/'로 분리
        bucket_name = url_parts[0]
        s3_key = url_parts[1]
        return bucket_name, s3_key

    # 섹션 추출 함수
    def extract_section(start_titles, end_titles, text):
        start_pattern = '|'.join([re.escape(start) for start in start_titles])
        end_pattern = '|'.join([re.escape(end) for end in end_titles])
        
        pattern = re.compile(rf"^(?:\s*)({start_pattern})(?:\s*)\n([\s\S]+?)(?=\n(?:\s*)({end_pattern})(?:\s*)|\Z)", re.MULTILINE)
        
        match = pattern.search(text)
        
        if match:
            return match.group(2).strip()  # 추출된 텍스트 반환
        else:
            return None

    # DB에서 URL 값 추출
    def get_s3_urls_from_db():
        cursor = connection.cursor()
        
        query = """
            SELECT id, s3_text_url 
            FROM wanted
            WHERE 
                ((responsibility IS NULL) + (qualification IS NULL) + (preferential IS NULL)) >= 2
                AND site = 'wanted'
        """
        
        cursor.execute(query)
        urls = cursor.fetchall()
        return urls  # [(id, s3_text_url)] 형식의 리스트 반환

    # DB 업데이트 쿼리 함수
    def update_job_info_in_db(job_id, key_tasks, requirements, preferred_qualifications):
        cursor = connection.cursor()

        # None 값을 NULL로 변환
        key_tasks = key_tasks if key_tasks else None
        requirements = requirements if requirements else None
        preferred_qualifications = preferred_qualifications if preferred_qualifications else None

        update_query = """
        UPDATE wanted 
        SET responsibility = %s, qualification = %s, preferential = %s 
        WHERE id = %s
        """
        cursor.execute(update_query, (key_tasks, requirements, preferred_qualifications, job_id))
        
    # 섹션 추출 설정
    sections_to_extract = {
        "주요업무": {
            "start_titles": ["주요업무"],
            "end_titles": ["자격요건", "▶ 서류전형 ▶ 면접전형 ▶ 건강검진 ▶ 최종합격"]
        },
        "자격요건": {
            "start_titles": ["자격요건"],
            "end_titles": ["우대사항", "혜택 및 복지"]
        },
        "우대사항": {
            "start_titles": ["우대사항"],
            "end_titles": ["혜택 및 복지"]
        }
    }
    # DB에서 URL 목록을 가져오기
    s3_urls = get_s3_urls_from_db()

    # MySQL 커서 한 번만 생성
    cursor = connection.cursor()

    # 각 URL에 대해 텍스트 파일을 읽고 섹션을 추출
    for job_id, url in s3_urls:
        try:
            bucket_name, s3_key = extract_s3_details(url)
            job_description = get_s3_file_content(bucket_name, s3_key)

            key_tasks = extract_section(sections_to_extract["주요업무"]["start_titles"], sections_to_extract["주요업무"]["end_titles"], job_description) or ""
            requirements = extract_section(sections_to_extract["자격요건"]["start_titles"], sections_to_extract["자격요건"]["end_titles"], job_description) or ""
            preferred_qualifications = extract_section(sections_to_extract["우대사항"]["start_titles"], sections_to_extract["우대사항"]["end_titles"], job_description) or ""

            print(f"Responsibility length: {len(key_tasks) if key_tasks else 0}")
            print(f"Qualification length: {len(requirements) if requirements else 0}")
            print(f"Preferential length: {len(preferred_qualifications) if preferred_qualifications else 0}")

            # 추출된 정보를 DB에 업데이트
            update_job_info_in_db(job_id, key_tasks, requirements, preferred_qualifications)

            # 출력
            print(f"URL: {url}")
            print(f"주요업무: {key_tasks}")
            print(f"자격요건: {requirements}")
            print(f"우대사항: {preferred_qualifications}")
            print("=" * 50)

        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    # MySQL 커밋 및 종료
    connection.commit()
    connection.close()

def incruit_txt():
    # S3 클라이언트 설정
    s3_client = boto3.client('s3')

    # S3 버킷에서 지정된 prefix(경로)에 있는 모든 파일 목록을 반환
    def list_s3_files(bucket_name, prefix):
        files = []
        continuation_token = None
        while True:
            params = {
                'Bucket': bucket_name,
                'Prefix': prefix
            }
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            
            response = s3_client.list_objects_v2(**params)
            files.extend([content['Key'] for content in response.get('Contents', [])])
            continuation_token = response.get('NextContinuationToken')
            if not continuation_token:
                break
        return files

    # S3에서 파일을 읽고 텍스트 추출
    def extract_text_from_s3_file(bucket_name, file_key, keyword_groups):
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        
        extracted_sections = {}
        for group in keyword_groups:
            section_name = group['section_name']
            start_keywords = group['start_keywords']
            end_keywords = group['end_keywords']
            
            start_index = None
            end_index = None
            section_text = ""
            
            for start in start_keywords:
                start_index = file_content.find(start)
                if start_index != -1:
                    break
            
            if start_index != -1:
                for end in end_keywords:
                    end_index = file_content.find(end, start_index)
                    if end_index != -1:
                        break
            
            if start_index != -1 and end_index != -1:
                section_text = file_content[start_index:end_index].strip()
            
            extracted_sections[section_name] = section_text
        
        return extracted_sections

    # S3 데이터를 처리하고 MySQL에 적재
    def process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn):
        # S3 버킷에서 텍스트 파일 목록 가져오기
        files = list_s3_files(bucket_name, prefix)
        cursor = conn.cursor()
        
        # max_length = 1000  # 최대 길이 설정

        for file_key in files:
            if file_key.endswith('.txt'):  # .txt 파일만 처리
                sections = extract_text_from_s3_file(bucket_name, file_key, keyword_groups)
                full_s3_url = "s3://t2jt/" + file_key  # S3 파일 URL 생성
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시각
                
                # 텍스트 길이 제한
                responsibility = sections.get('주요업무', '')
                qualification = sections.get('자격요건', '')
                preferential = sections.get('우대사항', '')
                
                # MySQL 데이터 삽입/업데이트
                cursor.execute("""
                    UPDATE incruit
                    SET update_time = %s, responsibility = %s, qualification = %s, preferential = %s
                    WHERE s3_text_url = %s
                    AND (responsibility IS NULL AND qualification IS NULL AND preferential IS NULL)
                """, (current_time, responsibility, qualification, preferential, full_s3_url))
        
        conn.commit()
        cursor.close()

    # 키워드 그룹 정의
    keyword_groups = [
        {
            "section_name": "주요업무",
            "start_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "[담당업무] ", "이런 업무를 해요", "담당업무 내용",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "# 담당업무 ",
                "  [우리는 이런일을 합니다]", "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", " 업무 내용 ", "직무소개",
            ],
            "end_keywords": [
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
                "[경력] 경력 3년 이내", "[핵심역량 및 기술]",
            ]
        },
        {
            "section_name": "자격요건",
            "start_keywords": [
                "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "[우리는 이런사람을 원합니다]", "기술스택",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 분들을 찾고 있어요", "# 자격요건", "자격 요건:", "필요역량 및 경험",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "필요역량 ", "  【자격요건】 이러한 분을 찾고 있어요",
                "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", "[필수 기술]", "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량 ", "지원자격 ", "지원자격",
                "  자격요건", "[필수 경험과 역량]", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ", "자격요건  ", "[Key Responsibilities]",
                "[기본조건]", "  [자격 요건]", "●  요구 경험", "자격사항", "□ 경력 요구사항", "[핵심역량 및 기술]",
            ],
            "end_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "담당업무 내용", "  [우리는 이런일을 합니다]", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]","# 담당업무 ",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", "[ 업무 안내 ]",
                "업무 내용:", " 업무 내용 ", "Project Manager", "[우대조건]", "저희가 우대하는 분들은 :  ",
                "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ",
                "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:", "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건",
                "근무시작일", "스킬", "[급여 조건]", "Place of Work ", "[기타]", "[ 제출서류 ]", "직무상세", "전형 절차", "전형절차", "기타 사항", "기타사항",
                "드론(조종) 촬영 보조", "경력/기술 요건:", "우대사항 ", "환경안전", "필요역량", "[모집 절차]", "우대사항  ", "우대사항-", "[지원 및 진행 절차]",
                " 복리후생", "근무시간", "근무지", "3. 투입시기", "■ 근무시간", "수행업무", "( 15명 )"," [이런 경험이 있으시면 더욱 좋아요]", " [꼭 확인해 주세요!]",
                "□ 우대사항", "□ 직무상세", "[우대사항]", "우대 사항",
            ]
        },
        {
            "section_name": "우대사항",
            "start_keywords": [
                "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ", "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:",
                "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건", "우대사항 ", "우대사항-", "[우대조건]", "저희가 우대하는 분들은 :  ",
                " [이런 경험이 있으시면 더욱 좋아요]", "□ 우대사항", "[우대사항]", "<우대>", "우대조건", "(우대)", "[ 우대 사항 ]"
            ],
            "end_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "# 담당업무 ", "담당업무 내용", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "  [우리는 이런일을 합니다]",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", " 업무 내용 ",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ",
                "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "필요역량 및 경험", "기술스택", "[필수 기술]",
                "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량", "지원자격 ", "  자격요건", "[필수 경험과 역량]", "자격요건  ",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 기술이 필요해요", "[우리는 이런사람을 원합니다]", "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "근무지", "# 자격요건","  【자격요건】 이러한 분을 찾고 있어요",
                "전형절차", "이런 조건에서 근무할 예정이에요", "○명", "근무조건", "스킬", "  【업무방향】 이러한 경험도 할 수 있어요", "혜택:", "혜택 및 복지", "기타사항",
                "제출서류", "▶ 지원서는 이렇게 작성하시면 좋아요", "[혜택 및 복지]", "지원자격", "측정", "기타 사항", "경력/기술 요건:", "●  요구 경험",
                "-----------------------------------------------------------------------", "[채용 전형 안내]", "BAT에 합류하는 여정", "기타 참고 사항", "Video Platform Team은 이런 팀입니다",
                "TSS > 기술컨설팅팀", "전형 절차 ", "전형 절차", "0명 ", "0명", "Full Stack Developer", "[모집 절차]", "[Key Responsibilities]", "[Application]",
                "○기타사항", "[근무 조건]", "[기본조건]", "기타사항 ㆍ사원~대리 직급 채용 희망", "[지원 및 진행 절차]", "  [자격 요건]", "재무팀 정규직", "지원 전 확인 부탁드립니다",
                "근무기간 : 6개월 (당사자 간 협의에 따라 연장 가능) / 인턴으로 3개월 근무 후 정규직 전환 평가", " 복리후생", "근무시간", "근무지", "■ 근무시간", "수행업무",
                "□ 기업문화 ", "자격사항", "근무조건 및 지원방법", " [꼭 확인해 주세요!]", "□ 경력 요구사항", "□ 직무상세", "[핵심역량 및 기술]",
            ]
        }
    ]

    # MySQL 연결 설정
    conn = pymysql.connect(
        host='43.201.40.223',          # AWS 퍼블릭 IP
        user='user',                   # MySQL 사용자
        password='1234',               # MySQL 비밀번호
        database='testdb',             # 데이터베이스 이름
        charset='utf8mb4'
    )

    # S3 버킷과 경로 지정
    bucket_name = 't2jt'
    prefix = 'job/DE/sources/incruit/txt/'  # S3에서 텍스트 파일이 있는 경로

    # 데이터 처리 및 MySQL로 바로 적재
    process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn)

    # MySQL 연결 종료
    conn.close()

def rocketpunch_txt():
    # S3 클라이언트 설정
    s3_client = boto3.client('s3')

    def list_s3_files(bucket_name, prefix):
        """S3 버킷에서 지정된 prefix(경로)에 있는 모든 파일 목록을 반환"""
        files = []
        continuation_token = None # list_objects_v2는 한번에 1000개만 갖고오니까 해당 token으로 위치 할당
        while True:
            params = {
                'Bucket': bucket_name,
                'Prefix': prefix
            }
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            
            response = s3_client.list_objects_v2(**params)
            files.extend([content['Key'] for content in response.get('Contents', [])])
            continuation_token = response.get('NextContinuationToken')
            if not continuation_token:
                break
        return files

    def extract_text_from_s3_file(bucket_name, file_key, keyword_groups):
        """S3에서 파일을 읽고 텍스트 추출"""
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        
        extracted_sections = {}
        for group in keyword_groups:
            section_name = group['section_name']
            start_keywords = group['start_keywords']
            end_keywords = group['end_keywords']
            
            start_index = None
            end_index = None
            section_text = ""
            
            for start in start_keywords:
                start_index = file_content.find(start)
                if start_index != -1:
                    break
            
            if start_index != -1:
                for end in end_keywords:
                    end_index = file_content.find(end, start_index)
                    if end_index != -1:
                        break
            
            if start_index != -1 and end_index != -1:
                section_text = file_content[start_index:end_index].strip()
            
            extracted_sections[section_name] = section_text
        
        return extracted_sections

    def process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn):
        """S3 데이터를 처리하고 MySQL에 적재"""
        # S3 버킷에서 텍스트 파일 목록 가져오기

        files = list_s3_files(bucket_name, prefix)
        cursor = conn.cursor()
        
        # max_length = 1000  # 최대 길이 설정

        for file_key in files:
            if file_key.endswith('.txt'):  # .txt 파일만 처리
                sections = extract_text_from_s3_file(bucket_name, file_key, keyword_groups)
                full_s3_url = "s3://t2jt/" + file_key  # S3 파일 URL 생성
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시각
                
                # 텍스트 길이 제한
                max_length = 3000  # 각 컬럼의 최대 길이 제한
                responsibility = sections.get('주요업무', '')
                qualification = sections.get('자격요건', '')
                preferential = sections.get('우대사항', '')

                # 길이 초과 시 "too long"으로 설정
                responsibility = "too long" if len(responsibility) > max_length else responsibility
                qualification = "too long" if len(qualification) > max_length else qualification
                preferential = "too long" if len(preferential) > max_length else preferential
                
                # MySQL 데이터 삽입/업데이트
                cursor.execute("""
                    UPDATE rocketpunch
                    SET update_time = %s, responsibility = %s, qualification = %s, preferential = %s
                    WHERE s3_text_url = %s
                    AND (responsibility IS NULL AND qualification IS NULL AND preferential IS NULL)
                """, (current_time, responsibility, qualification, preferential, full_s3_url))
        
        conn.commit()
        cursor.close()

    # 키워드 그룹 정의
    keyword_groups = [
        {
            "section_name": "주요업무",
            "start_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "[담당업무] ", "이런 업무를 해요", "담당업무 내용",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "주요업무", "주요 업무", "담당 업무", "담당업무",  "[주요 업무]", "[주요업무]", "# 담당업무 ",
                "  [우리는 이런일을 합니다]", "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", " 업무 내용 ", "직무소개",
            ],
            "end_keywords": [
                "자격요건", "자격 요건", "필수 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "자격 요건:", "필요역량 및 경험", "기술스택",
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
                "[경력] 경력 3년 이내", "[핵심역량 및 기술]",
            ]
        },
        {
            "section_name": "자격요건",
            "start_keywords": [
                "자격요건", "자격 요건", "필수자격", "필수 요건", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "[우리는 이런사람을 원합니다]", "기술스택",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 분들을 찾고 있어요", "# 자격요건", "자격 요건:", "필요역량 및 경험",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "필요역량 ", "  【자격요건】 이러한 분을 찾고 있어요",
                "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", "[필수 기술]", "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량 ", "지원자격 ", "지원자격",
                "  자격요건", "[필수 경험과 역량]", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ", "자격요건  ", "[Key Responsibilities]",
                "[기본조건]", "  [자격 요건]", "●  요구 경험", "자격사항", "□ 경력 요구사항", "[핵심역량 및 기술]",
            ],
            "end_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "담당업무 내용", "  [우리는 이런일을 합니다]", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]","# 담당업무 ",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", "[ 업무 안내 ]",
                "업무 내용:", " 업무 내용 ", "Project Manager", "[우대조건]", "저희가 우대하는 분들은 :  ",
                "우대사항", "우대 사항", "우대 요건", "우대요건", "우대 조건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ",
                "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:", "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건",
                "근무시작일", "스킬", "[급여 조건]", "Place of Work ", "[기타]", "[ 제출서류 ]", "직무상세", "전형 절차", "전형절차", "기타 사항", "기타사항",
                "드론(조종) 촬영 보조", "경력/기술 요건:", "우대사항 ", "환경안전", "필요역량", "[모집 절차]", "우대사항  ", "우대사항-", "[지원 및 진행 절차]",
                " 복리후생", "근무시간", "근무지", "3. 투입시기", "■ 근무시간", "수행업무", "( 15명 )"," [이런 경험이 있으시면 더욱 좋아요]", " [꼭 확인해 주세요!]",
                "□ 우대사항", "□ 직무상세", "[우대사항]", "우대 사항",
            ]
        },
        {
            "section_name": "우대사항",
            "start_keywords": [
                "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ", "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:",
                "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건", "우대 조건", "우대사항 ", "우대사항-", "[우대조건]", "저희가 우대하는 분들은 :  ",
                " [이런 경험이 있으시면 더욱 좋아요]", "□ 우대사항", "[우대사항]",
            ],
            "end_keywords": [
                "복지 및 혜택", "■ 근로형태", "인재영입 절차", "영입 절차", "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "# 담당업무 ", "담당업무 내용", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "산업분야", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "  [우리는 이런일을 합니다]",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", " 업무 내용 ",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ",
                "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "필요역량 및 경험", "기술스택", "[필수 기술]",
                "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량", "지원자격 ", "  자격요건", "[필수 경험과 역량]", "자격요건  ",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 기술이 필요해요", "[우리는 이런사람을 원합니다]", "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "근무지", "# 자격요건","  【자격요건】 이러한 분을 찾고 있어요",
                "전형절차", "이런 조건에서 근무할 예정이에요", "○명", "근무조건", "스킬", "  【업무방향】 이러한 경험도 할 수 있어요", "혜택:", "혜택 및 복지", "기타사항",
                "제출서류", "▶ 지원서는 이렇게 작성하시면 좋아요", "[혜택 및 복지]", "지원자격", "측정", "기타 사항", "경력/기술 요건:", "●  요구 경험",
                "-----------------------------------------------------------------------", "[채용 전형 안내]", "BAT에 합류하는 여정", "기타 참고 사항", "Video Platform Team은 이런 팀입니다",
                "TSS > 기술컨설팅팀", "전형 절차 ", "전형 절차", "0명 ", "0명", "Full Stack Developer", "[모집 절차]", "[Key Responsibilities]", "[Application]",
                "○기타사항", "[근무 조건]", "[기본조건]", "기타사항 ㆍ사원~대리 직급 채용 희망", "[지원 및 진행 절차]", "  [자격 요건]", "재무팀 정규직", "지원 전 확인 부탁드립니다",
                "근무기간 : 6개월 (당사자 간 협의에 따라 연장 가능) / 인턴으로 3개월 근무 후 정규직 전환 평가", " 복리후생", "근무시간", "근무지", "■ 근무시간", "수행업무",
                "□ 기업문화 ", "자격사항", "근무조건 및 지원방법", " [꼭 확인해 주세요!]", "□ 경력 요구사항", "□ 직무상세", "[핵심역량 및 기술]"
            ]
        }
    ]

    # MySQL 연결 설정
    conn = pymysql.connect(
        host='43.201.40.223',          # AWS 퍼블릭 IP
        user='user',                   # MySQL 사용자
        password='1234',               # MySQL 비밀번호
        database='testdb',             # 데이터베이스 이름
        charset='utf8mb4'
        )

    # S3 버킷과 경로 지정
    bucket_name = 't2jt'
    prefix = 'job/DE/sources/rocketpunch/txt/'  # S3에서 텍스트 파일이 있는 경로

    # 데이터 처리 및 MySQL로 바로 적재
    process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn)

    # MySQL 연결 종료
    conn.close()

def jobkorea_txt():
    # S3 클라이언트 설정
    s3_client = boto3.client('s3')

    def list_s3_files(bucket_name, prefix):
        """S3 버킷에서 지정된 prefix(경로)에 있는 모든 파일 목록을 반환"""
        files = []
        continuation_token = None
        while True:
            params = {
                'Bucket': bucket_name,
                'Prefix': prefix
            }
            if continuation_token:
                params['ContinuationToken'] = continuation_token
            
            response = s3_client.list_objects_v2(**params)
            files.extend([content['Key'] for content in response.get('Contents', [])])
            continuation_token = response.get('NextContinuationToken')
            if not continuation_token:
                break
        return files

    def extract_text_from_s3_file(bucket_name, file_key, keyword_groups):
        """S3에서 파일을 읽고 텍스트 추출"""
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read().decode('utf-8')
        
        extracted_sections = {}
        for group in keyword_groups:
            section_name = group['section_name']
            start_keywords = group['start_keywords']
            end_keywords = group['end_keywords']
            
            start_index = None
            end_index = None
            section_text = ""
            
            for start in start_keywords:
                start_index = file_content.find(start)
                if start_index != -1:
                    break
            
            if start_index != -1:
                for end in end_keywords:
                    end_index = file_content.find(end, start_index)
                    if end_index != -1:
                        break
            
            if start_index != -1 and end_index != -1:
                section_text = file_content[start_index:end_index].strip()
            
            extracted_sections[section_name] = section_text
        
        return extracted_sections

    def process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn):
        """S3 데이터를 처리하고 MySQL에 바로 적재"""
        # S3 버킷에서 텍스트 파일 목록 가져오기
        files = list_s3_files(bucket_name, prefix)
        cursor = conn.cursor()
        
        max_length = 1000  # 최대 길이 설정

        for file_key in files:
            if file_key.endswith('.txt'):  # .txt 파일만 처리
                sections = extract_text_from_s3_file(bucket_name, file_key, keyword_groups)
                full_s3_url = "s3://t2jt/" + file_key  # S3 파일 URL 생성
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 현재 시각
                
                # 텍스트 길이 제한
                responsibility = sections.get('주요업무', '')[:max_length]
                qualification = sections.get('자격요건', '')[:max_length]
                preferential = sections.get('우대사항', '')[:max_length]
                
                # MySQL 데이터 삽입/업데이트
                cursor.execute("""
                    UPDATE jobkorea
                    SET responsibility = %s, qualification = %s, preferential = %s
                    WHERE s3_text_url = %s
                    AND (responsibility IS NULL AND qualification IS NULL AND preferential IS NULL)
                """, (responsibility, qualification, preferential, full_s3_url))
        
        conn.commit()
        cursor.close()

    # 키워드 그룹 정의
    keyword_groups = [
        {
            "section_name": "주요업무",
            "start_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "[담당업무] ", "이런 업무를 해요", "담당업무 내용",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "# 담당업무 ",
                "  [우리는 이런일을 합니다]", "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", " 업무 내용 ", "직무소개", "업무 상세",
            ],
            "end_keywords": [
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
                "지원 방법 및 채용 절차", "요구 사항", "우대 조건", "우대조건]", "[ Bigdata Engineer로 이런 분이 필요합니다 ]"
            ]
        },
        {
            "section_name": "자격요건",
            "start_keywords": [
                "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "[우리는 이런사람을 원합니다]", "기술스택",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 분들을 찾고 있어요", "# 자격요건", "자격 요건:", "필요역량 및 경험",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "필요역량 ", "  【자격요건】 이러한 분을 찾고 있어요",
                "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", "[필수 기술]", "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량 ", "지원자격 ", "지원자격",
                "  자격요건", "[필수 경험과 역량]", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ", "자격요건  ", "[Key Responsibilities]",
                "[기본조건]", "  [자격 요건]", "●  요구 경험", "자격사항", "□ 경력 요구사항", "[핵심역량 및 기술]", "기본자격", " [자격요건]", "자격조건",
                "[ Bigdata Engineer로 이런 분이 필요합니다 ]"
            ],
            "end_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "담당업무 내용", "  [우리는 이런일을 합니다]", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]","# 담당업무 ",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", "[ 업무 안내 ]",
                "업무 내용:", " 업무 내용 ", "Project Manager", "[우대조건]", "저희가 우대하는 분들은 :  ",
                "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ",
                "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:", "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건",
                "근무시작일", "스킬", "[급여 조건]", "Place of Work ", "[기타]", "[ 제출서류 ]", "직무상세", "전형 절차", "전형절차", "기타 사항", "기타사항",
                "드론(조종) 촬영 보조", "경력/기술 요건:", "우대사항 ", "환경안전", "필요역량", "[모집 절차]", "우대사항  ", "우대사항-", "[지원 및 진행 절차]",
                " 복리후생", "근무시간", "근무지", "3. 투입시기", "■ 근무시간", "수행업무", "( 15명 )"," [이런 경험이 있으시면 더욱 좋아요]", " [꼭 확인해 주세요!]",
                "□ 우대사항", "□ 직무상세", "[우대사항]", "우대 사항", "[우대조건]", "근무 시간 및 장소", "지원 방법 및 채용 절차", "업무 상세", "요구 사항",
                "우대 조건", "우대조건]",
            ]
        },
        {
            "section_name": "우대사항",
            "start_keywords": [
                "우대사항", "우대 사항", "우대 요건", "우대요건", "이런 분이면 더 좋아요", "[우대사항]", "[우대 사항]", "[우대 요건]", "[우대요건]", "# 우대사항 ", "  【우대사항】 이러한 분이면 더욱 좋아요", "우대 사항:",
                "이런 분이 오시면 좋아요 [우대사항]", "Benefits ", "우대경험/역량", " 우대조건", "우대사항 ", "우대사항-", "[우대조건]", "저희가 우대하는 분들은 :  ",
                " [이런 경험이 있으시면 더욱 좋아요]", "□ 우대사항", "[우대사항]", "요구 사항", "우대 조건", "우대조건]", "[ Bigdata Engineer로 이런 분을 우대합니다 ]",
            ],
            "end_keywords": [
                "합류하면 함께 할 업무예요", "이런 일을 함께하고 싶습니다.", "담당 업무는 다음과 같습니다.", "[담당업무]", "[담당 업무]", "# 담당업무 ", "담당업무 내용", "[담당업무] ",
                "함께 담당하게 될 업무입니다", "Key Responsibilities", "담당 업무", "담당업무", "주요업무", "주요 업무", "[주요 업무]", "[주요업무]", "  [우리는 이런일을 합니다]",
                "담당업무 ", " 담당업무", "담당 업무 ", " 담당 업무", "  【업무소개】 이러한 일을 해요", "주요 업무: ", "이런 업무를 해요 [주요 업무]", " 업무 내용 ",
                "직무상세", "[ 업무 안내 ]", "업무 내용:", "지원자격(필수)", "필수 경험과 역량 ", "자격요건 ", "[필수자격요건]", "필요 자격 및 기술 ",
                "자격요건", "자격 요건", "필수자격", "필수 자격", "필요 역량", "필요역량", "Required Qualifications", "필요역량 및 경험", "기술스택", "[필수 기술]",
                "필수사항", "지원 자격", "[ 필수(자격) 조건 ]", "경험/역량", "지원자격 ", "  자격요건", "[필수 경험과 역량]", "자격요건  ",
                "Bigdata Engineer로 이런 분이 필요합니다", "이런 분과 함께하고 싶습니다.", "이런 기술이 필요해요", "[우리는 이런사람을 원합니다]", "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]",
                "이런 역량을 가지신 분을 찾습니다.", "이런 분과 함께하고 싶어요", "[자격요건]", "[자격 요건]", "근무지", "# 자격요건","  【자격요건】 이러한 분을 찾고 있어요",
                "전형절차", "이런 조건에서 근무할 예정이에요", "○명", "근무조건", "스킬", "  【업무방향】 이러한 경험도 할 수 있어요", "혜택:", "혜택 및 복지", "기타사항",
                "제출서류", "▶ 지원서는 이렇게 작성하시면 좋아요", "[혜택 및 복지]", "지원자격", "측정", "기타 사항", "경력/기술 요건:", "●  요구 경험",
                "-----------------------------------------------------------------------", "[채용 전형 안내]", "BAT에 합류하는 여정", "기타 참고 사항", "Video Platform Team은 이런 팀입니다",
                "TSS > 기술컨설팅팀", "전형 절차 ", "전형 절차", "0명 ", "0명", "Full Stack Developer", "[모집 절차]", "[Key Responsibilities]", "[Application]",
                "○기타사항", "[근무 조건]", "[기본조건]", "기타사항 ㆍ사원~대리 직급 채용 희망", "[지원 및 진행 절차]", "  [자격 요건]", "재무팀 정규직", "지원 전 확인 부탁드립니다",
                "근무기간 : 6개월 (당사자 간 협의에 따라 연장 가능) / 인턴으로 3개월 근무 후 정규직 전환 평가", " 복리후생", "근무시간", "근무지", "■ 근무시간", "수행업무",
                "□ 기업문화 ", "자격사항", "근무조건 및 지원방법", " [꼭 확인해 주세요!]", "□ 경력 요구사항", "□ 직무상세", "[핵심역량 및 기술]","기본자격",
                " [자격요건]", " [직무경험]", "근무 시간 및 장소", "자격조건", "지원 방법 및 채용 절차", "업무 상세",
            ]
        }
    ]


    # MySQL 연결 설정
    conn = pymysql.connect(
        host='43.201.40.223',          # AWS 퍼블릭 IP
        user='user',                   # MySQL 사용자
        password='1234',               # MySQL 비밀번호
        database='testdb',             # 데이터베이스 이름
        charset='utf8mb4'
    )

    # S3 버킷과 경로 지정
    bucket_name = 't2jt'
    prefix = 'job/DE/sources/jobkorea/txt/'  # S3에서 텍스트 파일이 있는 경로

    # 데이터 처리 및 MySQL로 바로 적재
    process_and_insert_into_db(bucket_name, prefix, keyword_groups, conn)

    # MySQL 연결 종료
    conn.close()

def saramin_txt():
    # S3 및 DB 설정
    BUCKET_NAME = "t2jt"
    SARAMIN_TEXT_PATH_PREFIX = "job/DE/sources/saramin/txt/"
    DB_CONFIG = {
        'host': '43.201.40.223',
        'user': 'user',
        'password': '1234',
        'database': 'testdb',
        'port': '3306'
    }

    # S3 클라이언트 생성
    s3_client = boto3.client('s3')

    # MySQL 연결 풀 설정
    connection_pool = pooling.MySQLConnectionPool(pool_name="saramin_pool", pool_size=5, **DB_CONFIG)


    def get_connection():
        """데이터베이스 연결을 가져옵니다."""
        return connection_pool.get_connection()


    def read_s3_file(bucket_name, s3_key):
        """S3에서 파일을 읽어 내용을 반환합니다."""
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
            return response['Body'].read().decode('utf-8')
        except Exception as e:
            print(f"S3 파일 읽기 오류: {s3_key}, 에러: {e}")
            return None

    def extract_sections(content):
        """텍스트에서 키워드 사이의 값을 정확히 추출합니다."""
        try:
            # 키워드 리스트 정의
            # 주요 업무
            responsibility_start_keywords = ["주요업무", "ㅣ 담당 업무", "[주요 업무]", "담당업무", "[주요업무]", "[담당업무]", "모집부문 : 데이터플랫폼 엔지니어", "[주요업무]", "설비혁신부문", " [담당업무]", "경력 소프트웨어 엔지니어 담당업무", "담당업무 Field Team 1명", "담당 업무", "2. 담당업무", "| 주요 업무", "주요 업무", "업무내용", "[담당업무 및 필요경험]", "(신입)", "[담당업무] ", "데이터 엔지니어", "담당업무", "이러한 업무를 수행합니다.", "데이터 플랫폼 엔지니어", "o 담당 업무", "       정비기술본부 주요업무   ", "Responsibilities", "QA팀(품질보증팀) 담당 업무", "기술 지원", "담당업무 (개발 직무 아님)", "모집부문 담당업무 자격요건 우대사항", " ※ 담당업무", " 이러한 업무를 수행합니다.", "*.Data Scientist는,", "시스템", "이런 업무를 해요 (주요 업무)", "이런 업무를 해요 (주요 업무) ", "수행업무", "근무지: 메가존산학연센터", "ㆍ기술 : Windows, Linux 서버 관리 기술", "| 합류하면 담당할 업무예요", "모집분야", "(신입/경력)", "[업무내용]", "\bDBA 영입", "✔ 이런 업무를 담당합니다", "[Responsibilities]", "엔지니어 [ 주요업무 ]", "근무지: 메가존산학연센터", "[담당 업무]", "[ 담당업무 ]", "[우리는 이런 일을 합니다]", "경력 3년 이상 15년이하", "▶ 담당업무", "담당업무 자격요건 및 우대사항", "  ■ 담당업무", "0명 모집 분야", "✔ 이런 일을 합니다.", "Client Engineer (iOS/Android)", "SI 프로젝트)", "업무분야", "근무지: 역삼역 인근", "<담당업무>", "솔루션 엔지니어 (시스템 엔지니어) 사업2본부 1명", "| 합류하면 담당할 업무예요", "[이런 일을 합니다.]", "※ 입사하게 되면 함께 할 >업무에요", "모집부문", "■ 업무내용", "※ 모집부문", "[Responsibilities]", "# 업무 내용", "▶ 주요업무 분야", "[업무]", "구분 상세내용", "구분 세부내용", "● 주요업무", "다음과 같은 일들을 하시게 됩니다.", "% 담당업무", "# 담당 업무", "비즈니스 컨설턴트 (Data 분석)", "하시게 될 일 :", "[DELIVERABLES]", " 업무 내용", "역할:", "   - 프로젝트 과정에서 어떤 도전과 성장을 이루었는지 구체적으로 설명해주세요.", "Responsibilities:", "포지션", "◈담당 업무◈", "• 채용분야", "[ 주요 담당 업무 ]  ", "▶ 주요업무 분야", "2. 담당 업무", "솔루션 개발 / 프로젝트 수행", "합류하면 함께 할 업무에요", "●담당 업무 ", "기술 본부에서 함께 할 업무", "    | 주요 업무", "√ 주요업무", "■ 담당업무", "■담당업무", "1) 담당업무", "이런 일을 하실 거에요", "(7년~15년)", "담당업무(신입)", "담당자", "이런 업무를 해요 [주요 업무]", "* 담당 업무 ", "*** 저희와 함께 할 업무에요 ***", "02.담당하시게 될 업무를 소개합니다.", "모집 부문 담당 업무 지원 자격", "모집분야 담당업무 자격요건", "업무 내용", "[ Responsibilities ]", "(담당업무)", "✅ What’s in it for you? (Responsibilities)", "1. 담당업무", " 【업무소개】 이러한 일을 해요", "미들웨어 중급 1명"]
            responsibility_end_keywords = ["지원자격", " ㅣ 지원자격", "[근무 조건]", "우대사항", "자격요건", "[자격요건]", "[지원자격]", "[필수자격]", "근무조건", "[근무지] 서울시 성동구", "자격 요건", " [자격요건]", "취급제품", "자격요건", "3. 자격요건", "| 자격요건", "자격요건", "[우대사항]", "ㆍ클라우드 기반 시스템 관리 설계 및 운영 [필수 자격 조건]", "- BigQuery 등 데이터 웨어하우스 관련 경험", "자격요건", "이러한 역량과 경험이 있는 분들을 찾습니다.", "- 클라우드 환경 구축 경험", "자격 요>건 ", "o 필요기술 및 우대사항(관련 경력)", "모집부문 상세내용", "Qualifications", "지원 자격요건", "- 관련 경력 3년 이상", "경력 3년 이상", "ㅣ자격사항", "* 이런 분이 필요해요!", "이런 분들을 찾고 있어요 (자격 요건)", " 이런 분들을 찾고 있어요 (자격 요건)", "| 이런 분과 함께 하고 싶어요", "자격 요건 0명", "자격요건 및 자격 (상세요건 및 우대사항)", "[필수조건]", "- 자격요건 - MySQL 운영 경험 있으신 분 (설치, 백업복구, HA, DR 등)", "✔ 이런 역량을 갖춘 분을 찾습니다", "[Requirements]", "[ 지원자격 ]", "[필요 자격]", "[ 우대사항 ]", "[우리는 이런 사람을 원합니다]", "[기술스택]", "3. 2개부문 공통 우대사항", "▶ 자격요건", "[ 자격요건 ]", "✔ 이런 분을 찾고 있어요.", "[자격 요건]", "ㆍ 근무지역 : 대신파이낸스센터", "<우대사항>", " ㆍ요구사항", " | 이런 분과 함께 하고 싶어요", "[이런 분을 찾습니다.]", "※ 이런 분을 찾고 있어요", "지원자격 ㆍ학력 : 무관", "[필수 경험과 역량]", "■ 필수사항", "※ 근무지역", "[Qualifications]", "# 지원 자격", "▶ 이런 분이면 더 좋아요 (신입, 경력 남, 여 공통)", "[필수역량] (중 1개에 해당해도 지원가능)", "자격요건 ㆍMYSQL DB 운영 경험이 2년 이상 있는 분", "자격요건 ㆍ백엔드 경력 3년 이상 5년 미만이신 분", "[우대역량]", "● 자격요건", "이러한 분들을 찾고 있습니다.", "2. 필수자격요건", "# 필수 역량","      - Consultancy를 바탕으로 한 문제해결 및 Communication 역량", "주로 다룰 소프트웨어 :", "[KEY INTERFACES]", " 자격 요건", "자격 요건:", "자격요건 ㆍ0년~4년 개발 경력", "Qualifications:", "자격요건 ㆍ학력 : 대졸 2,3년 이상", "◈자격 요건◈", "• 자격요건", "[ 이런 분을 모시고 있어요 ]  ", "▶ 이런 분이면 더 좋아요 (신입, 경력 남, 여 공통)", "3. 필수 자격요건", "자격요건 - 학력 : 무관", "이러한 경험을 할 수 있어요", "●자격 요건", "  |  자격 요건 ", "√ 자격요건", "■ 근무환경", "■자격요건", "2) 자격요건", " 이런 분을 찾아요", "자격요건 및 우대사항", "2. 지원자격", "필수역량", "※ 자격요건", "자격요건 ㆍ개발 및 기술에 대한 폭넓은 이해를 가지고 있는 분", "■ 자격요건", "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", " *  자격 요건 ", "*** 이>런 분을 찾고 있어요 ***", "03.이런 경험을 가진 분과 성장하고 싶습니다.", "[ 필수 요건 ]", "ㆍ근무형태 : 정규직", "이런 사람을 찾아요!", "[ Basic Qualifications ]", "(자격요건)", "✅ Are you the one we’re looking for? (Qualifications)", "2. 근무지", " 【기술스택】 이러한 툴을 활용해요", "-필수요건: JEUS, WebtoB, Apache, Tomcat 운영 경험"]
            # 자격 요건
            qualification_start_keywords = ["지원자격", " ㅣ 지원자격", "[자격 요건]", "자격요건", "[자격요건]", "[지원자격]", "-필수요건:", "[필수자격]", "지원자격", "공통 자격요건", "[지원자격]", "<지원자격>", "모집부문 담당업무 자격요건", "공통요건", " [자격요건]", "주요요건", "자격 요건", "3. 자격요건", "| 자격요건", "ㆍ클라우드 기반 시스템 관리 설계 및 운영 [필수 자격 조건]", "- 마케팅 솔루션에서 제공된 API로 데이터를 적재", "이러한 역량과 경험이 있는 분들을 찾습니다.", "- 데이터 플랫폼 구축 및 운영", "o 자격요건", "자격요건", "공통 자격요건 및", "Qualifications", "지원 자격요건", "   니어", "Teams, Microsoft Back Office 구축 및 기술 지원", "ㅣ자격사항", "* 이런 분이 필요해요!", "이런 분들을 찾고 있어요 (자격 요건)", " 이런 분들을 찾고 있어요 (자격 요건)", "| 이런 분과 함께 하고 싶어요", "[필요기술]", "[필수조건]", "- 데이터 이관 및 마이그레이션", "✔ 이런 역량을 갖춘 분을 찾습니다", "필요역량", "[Requirements]", "[ 지원자격 ]", "필요역량", "[우리는 이런 사람을 원합니다]", "- 자격요건 및 우대사항", "▶ 자격요건", "[ 자격요건 ]", "■ 지원자격", "✔️이런 분을 찾고 있어요.", "[필요 역량 및 직무 경험]", "<지원자격>", " ㆍ요구사항", " | 이런 분과 함께 하고 싶어요", "[이런 분을 찾습니다.]", "※ 이런 분을 찾고 있어요", "[필수 경험과 역량]", "■ 필수사항", "※ 지원자 요건", "[Qualifications]", "# 지원 자격", "▶ 이런 분이면 더 좋아요 (신입, 경력 남, 여 공통)", "ㆍ데이터웨어하우스 설계 및 구축, 운영", "ㆍ리눅스 컨테이너 기반의 코드 실행 서비스를 개발하고 고도화합니다.", "[자격요건]", "● 자격요건", "이러한 분들을 찾고 있습니다.", "2. 필수자격요건", "# 필수 역량", "이런 분을 원합니다 :", "[EDUCATION]", " 자격 요건", "자격 요건:", "ㆍAI 기능을 통합한 UI/UX 개발 및 구현", "Qualifications:", "ㆍ제품 소개, 교육, PoC, BMT, 사업 제안 등", "◈자격 요건◈", "• 자격요건", "[ 이런 분을 모시고 있어요 ]  ", "3. 필수 자격요건", "담당업무 - 이메일솔루션개발 및 유지보수", "이런 분과 함께 하고 싶어요", "●자격 요건", "  |  자격 요건 ", "√ 자격요건", "■ 자격요건", "■자격요건", "2) 자격요건", " 이런 분을 찾아요", "자격요건 및 우대사항", "2. 지원자격", "필수역량", "※ 자격요건", "   기술적인 합의점을 도출합니다.", "이런 자격을 갖춘 분을 찾고 있어요 [자격 요건]", " *  자격 요건 ", "*** 이런 분을 찾고 있어요 ***", "03.이런 경험을 가진 분과 성장하고 싶습니다.", "[ 필수 요건 ]", "이런 사람을 찾아요!", "[ Basic Qualifications ]", "(자격요건)", "✅ Are you the one we’re looking for? (Qualifications)", " 【기술스택】 이러한 툴을 활용해요"]
            qualification_end_keywords = ["우대사항", " [ 우대 사항 ]", "[우대 사항]", "담당업무", "[우대사항]", "[우대조건] ", "-기간:", "[우대사항]", "근무지역", "주요업무", "근무조건", "<근무지> 판교", "근무조건", "우대요건", " [우대사항]", "근무지: 경기도", "우대 사항", "4. 팀 구성", "| 우대 사항", " 우대요건", "- 관련 자격증 보유하신 분 (Cloud, RDB, SQL, Bigdata, IT 개발 관련)", "우대사항 ㆍGA(구글 애널리틱스), GTM(구글 태그매니저) 사용 경험", "이러한 강점이 있다면 더욱 좋습니다.", "- Crawling 개발 및 운영 경험 (IP / 로봇 차단 우회 경험)", "o 담당 업무", "우대조건", "- 하드웨어 개발", "※ 근무지 : 서울", "이런 분이면 더 좋아요", "- Microsoft 관련 기술 자격증 보유자", "Microsoft O365 / M365 유경험자", "ㅣ근무조건", "* 이런 경험이 있으면 더 좋아요!", "우대 조건", "이런 분이면 더 좋아요 (우대 사항)", " | 이런 분이면 더 좋아요", "근무조건", "[우대조건]", "- 우대사항 - 데이터 표준화 관리 경험이 있으신 분", "✔ 이런 역량이 있으면 더욱 좋습니다", "[Preferred Qualifications]", "필수 >제출사항", "[우대요건]", "[ 우대사항 ]", "2.. 시스템엔지니어", "▶ 우대사항", "[ 우대사항 ]", "  ■ 우대사항", "✔ 이런 분이면 더 좋아요.", "  ㆍ우대사항", " | 이런 분이면 더 좋아요", "[이런 경험이 있다면 더욱 좋습니다.]", "※ 이런 분이면 더 좋아요", "[채용 전형 안내]", "■ 우대사항", "모집부문", "[Preferred Skills]", "# 우대 사항", "▶ 함께하면 받는 혜택 및 복지", "[업무]", "우대사항 ㆍ서비스 DB 설계 및 구축 경험 있는 분", "우대사항 ㆍLinux 환경에서 시스템 개발/운영 경험이 있으신 분", "● 우대사>항", "이런 경험이 있으시면 더욱 좋습니다", "3. 우대사항", "저희가 우대하는 분들은 :", "[SKILLS]", "*영문이력서 제출", "우대 사항:", "우대사항 ㆍ기본적인 테스트 작성 경험 (Cypress, Jest, React Testing Library 등)", "Are you a trailblazing Software Engineer who regards yourself as an expert in C# and/or Python?", "업무환경 ㆍ사내 LAB (팔로알토,F5 등) 및 클라우드(AWS, Azure, GCP) 테스트 환경이 마련되어 있어", "◈우대 사항◈", "• 우대사항", "[ 이런 분이면 더욱 좋아요 ]  ", "4. 우대사항", "우대사>항 - 관련 학과 전공자", "이런 경험이 있다면 더 좋아요", "●우대 사항", "주요 및 복지", "  |  공통요건 ", "√ 우대사항", "■ 우대사항", "■우대사항", "3) 우대사항", " 이런 경험이 있으면 더 좋아요", "Benefits", "3. 우대사항", "※ 우대사항", "우대사항 ㆍPO/PM, BE/FE 엔지니어 등 다양한 직군의 동료들과의 협업을 경험해 보신 분", "#인재상", "이런 분이 오시면 좋아요 [우대 사항]", "         *  우대 사항", "*** 이런 분이면 더 좋아요 ***", "04.이런 분이면 더욱 좋습니다.", "[ 우대 사항 ]", "이런 사람이면 더 좋아요", "[ Preferred Qualifications ]", "(우대사항)", "✅ Here at Nimbyx, we offer you the best to be the best!", " 【우대사항】 이러한 분이면 더욱 좋아요"]
            # 우대 사항
            preferential_start_keywords =["우대사항", " [ 우대 사항 ]", "[우대 사항]", "[우대사항]", "[우대조건] ", "[우대사항]", "우대요건", " [우대사항]", "우대 사항", "| 우대 사항", "우대요건", "- 관련 자격증 보유하신 분 (Cloud, RDB, SQL, Bigdata, IT 개발 관련)", "ㆍ자바스크립트 / 리눅스 사용 및 개발 경험자", "- SQL 중급 이상", "o 필요기술 및 우대사항(관련 경력)", "우대조건", "이런 분이면 더 좋아요", "   지식이 있는 분", "Microsoft 365 구축 또는 기술지원 가능자", "* 이런 경험이 있으면 더 좋>아요!", "우대 조건", "이런 분이면 더 좋아요 (우대 사항)", "| 이런 분이면 더 좋아요", "[우대조건]", "- Docker 및 k8s 환경이 익숙하신 분", "✔ 이런 역량이 있으면 더욱 좋습니다", "[Preferred Qualifications]", "[우대요건]", "[ 우대사항 ]", "3. 2개부문 공통 우대사항", "▶ 우대사항", "[ 우대사항 ]", "이러한 강점이 있다면 더욱 좋습니다.", "  ■ 우대사항", "✔ 이런 분이면 더 좋아요.", "<우대사항>", "  ㆍ우대사항", "있으면 좋은 우대사항 (우대사항은 보유하지 않아도 지원 가능합니다.)", " | 이런 분이면 더 좋아요", "[이런 경험이 있다면 더욱 좋습니다.]", "※ 이런 분이면 더 좋아요", "■ 우대사항", "※ 우대사항", "[Preferred Skills]", "# 우대 사항", "[우대역량]", "ㆍ여러 동료들과 적극적으로 소통하며 협업할 수 있는 분", "ㆍGit 등의 버전 관리 시스템 경험이 있으신 분", "● 우대사항", "# 우대", "이런 경험이 있으시면 더욱 좋습니다", "3. 우대사항", "# 우대 사항", "저희가 우대하는 분들은 :", "우대 사항:", "ㆍ스스로 문제를 정의하고, 주도적으로 해결하는 태도", "◈우대 사항◈", "• 우대사항", "[ 이런 분이면 더욱 좋아요 ]  ", "▶ 이런 분이면 더 좋아요 (신입, 경력 남, 여 공통)", "4. 우대사항", "- 포트폴리오 必", "이런 경험이 있다면 더 좋아요", "●우대 사항", "√ 우대사항", "■ 우대사항", "■우대사항", "3) 우대사항", " 이런 경험이 있으면 더 좋아요", "3. 우대사항", "※ 우대사항", "   파악하고 해결할 수 있는 분", "이런 분이 오시면 좋아요 [우대 사항]", "이런 분이 오시면 좋아요 [우대 사항]", "         *  우대 사항", "*** 이런 분이면 더 좋아요 ***", "04.이런 분이면 더욱 좋습니다.", "[ 우대 사항 ]", "이런 사람이면 더 좋아요", "[ Preferred Qualifications ]", "(우대사항)", "✅ Here at Nimbyx, we offer you the best to be the best!", " 【우대사항】 이러한 분이면 더욱 좋아요"]
            preferential_end_keywords = ["근무조건", "경력과 매칭되시는 분은", "함께하기 위한 방법", "근무조건", "마감일 및 근무지", "업무 상세", "[근무지]", "[복리후생]", "02. 급여 및 근무조건", "복지 및 혜택", "주요업무", "[주요업무]", "■ 급 여", "근무환경", "  [근무지]", "[복리후생]", "| 기타 사항", "혜택", "전형 절차", "함께하기 위한 방법", "(성수)&", "접수방법 - 사람인 온라인 입사지원", "※ 장애인은 관련 법령에 의하여 채용시 우대합니다", "근무지 ㆍ본사(성수)&프로젝트 파견지", "데이터 엔지니어", "회사사진  ", "혜택 및 복지", "- 하드웨어 개발", "함께하면 받는 혜택 및 복지", "복리후생", "근무형태 : 정규직 (수습기간 3개월)", "*.Data Platform Engineer에 지원하고 싶다면 아래의 서류를 제출해 주세요.", "[꼭 읽어 주세요!]", "접수 및 절차", "지원서는 이렇게 작성하시면 좋아요", "전형안내", "※근무지 주소: 경기도 과천시 과천대로7길 74(갈현동, 메가존산학연센터)", "| 이렇게 합류해요", "사용 기술", "- 접수방법 온라인 공고 입사지원", "✔ 아래 여정을 통해 합류합니다", "함께하기 위한 방법", "근>무조건 및 환경", "       근무조건", "※근무지 주소: 경기도 과천시 과천대로7길 74(갈현동, 메가존산학연센터)", "사용기술", "  근무조건", "- 호스팅 업체 근무 경험자", "근무조건은 확인해주세요", "[근무조건]", "4. 이런분들은 지원하지 마세요 정중하게 거절합니다", "채용 정보는 아래와 같습니다.", "8) 운전가능하신 분 서울 대방", "  ■ 담당업무", "✔ 이런 분이면 더 좋아요.", "[채용 전형 안내]", "기타사항", "근무지: 역삼역 인근", "<지원자격>", "접수기간 및 방법", "지원 시 참고사항", "업무환경", " | 이렇>게 합류해요", "[이러한 일정으로 진행됩니다.]", "※ 함께하면 받는 혜택 및 복지", "※ 근무지 : 성남 본사(남위례역)", "[What We Offer]", "# 복리후생", "근무환경 및 기타", "※ 신입 또는 비 동종업계 경력자의 경우 회사 사업분야의 기술교육을 이수해야함", "# 알아두기", "마크비전에서 사용하는 기술스택입니다.", "4. 지원 방법", "# 지원자격", "부산/영남", "채용 절차:", "기술스택 ㆍES6+, React 16+, TypeScript 로 웹 Application 구현", "◈전형 절차◈", "• 근무형태 : 정규직", "[ 근무 조건 ]  ", "▶ 함께하면 받는 혜택 및 복지", "5. 지원 방법", "합류 여정은 다음과 같아요", "●근무 조건", "√ 혜택 및 복지", "■ 담당업무", "■근무조건", "4) 복지 및 혜택", "이런 툴을 사용해요", "Why", "………………………………………………………………………………………………………………………………", "공통자격", "우리 회사 복지는요.", "□ 수습기간", "▶ 지원서는 이렇게 작성하시면 좋아요", "전형절차", "*** 조직문화를 함께 만들어가요 ***", "05.근무조건", "[필수 사항]", "복지", "함께하기 위한 방법", "(복지)", "If you’re ready to ditch the corporate monotony, embrace the awesome, and lead the future of AI innovation in Korea, Nimbyx is your stage!", " 【업무방향】 이러한 경험도 할 수 있어요"]

            # 정확히 키워드와 일치하는지 확인하는 함수
            def exact_match_keywords(line, keywords):
                return line.strip() in keywords

            # 텍스트를 라인 단위로 처리
            lines = content.splitlines()

            responsibility = None
            qualification = None
            preferential = None

            # 라인별로 처리
            for i, line in enumerate(lines):
                # 주요업무 추출
                if responsibility is None and exact_match_keywords(line, responsibility_start_keywords):
                    for j in range(i + 1, len(lines)):
                        if exact_match_keywords(lines[j], responsibility_end_keywords):
                            responsibility = "\n".join(lines[i + 1:j]).strip()
                            break

                # 자격요건 추출
                if qualification is None and exact_match_keywords(line, qualification_start_keywords):
                    for j in range(i + 1, len(lines)):
                        if exact_match_keywords(lines[j], qualification_end_keywords):
                            qualification = "\n".join(lines[i + 1:j]).strip()
                            break

                # 우대사항 추출
                if preferential is None and exact_match_keywords(line, preferential_start_keywords):
                    for j in range(i + 1, len(lines)):
                        if exact_match_keywords(lines[j], preferential_end_keywords):
                            preferential = "\n".join(lines[i + 1:j]).strip()
                            break

                # 모든 섹션을 추출했으면 종료
                if responsibility and qualification and preferential:
                    break

            return responsibility, qualification, preferential
        except Exception as e:
            print(f"텍스트 추출 오류: {e}")
            return None, None, None

    def update_database(record_id, responsibility, qualification, preferential):
        """DB에서 해당 행의 칼럼을 업데이트합니다."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            update_query = """
                UPDATE saramin
                SET responsibility = %s, qualification = %s, preferential = %s, update_time = %s
                WHERE id = %s
            """
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(update_query, (responsibility, qualification, preferential, current_time, record_id))
            conn.commit()
            print(f"ID {record_id} 업데이트 성공.")
        except Exception as e:
            print(f"DB 업데이트 실패: ID {record_id}, 에러: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def process_records():
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            select_query = """
                SELECT id, s3_text_url, responsibility, qualification, preferential
                FROM saramin
                WHERE s3_text_url IS NOT NULL
                ORDER BY id ASC
            """
            cursor.execute(select_query)
            records = cursor.fetchall()

            if not records:
                print("조회된 레코드가 없습니다.")
                return

            for record in records:
                record_id = record['id']
                s3_url = record['s3_text_url']

                # S3 URL 유효성 검사
                if not s3_url or not s3_url.startswith(f"s3://{BUCKET_NAME}/"):
                    print(f"ID {record_id}: 잘못된 S3 URL 혹은 images URL. 건너뜁니다.")
                    continue

                # S3 텍스트 읽기
                s3_key = s3_url.split(f"s3://{BUCKET_NAME}/")[1]
                saramin_content = read_s3_file(BUCKET_NAME, s3_key)
                if not saramin_content:
                    print(f"ID {record_id}: S3 파일을 읽을 수 없습니다. 건너뜁니다.")
                    continue

                # 텍스트 섹션 추출
                responsibility_text, qualification_text, preferential_text = extract_sections(saramin_content)

                # 업데이트 확인 및 로깅
                if record['responsibility'] is not None:
                    print(f"ID {record_id}: Responsibility 칼럼이 이미 채워져 있습니다. 건너뜁니다.")
                if record['qualification'] is not None:
                    print(f"ID {record_id}: Qualification 칼럼이 이미 채워져 있습니다. 건너뜁니다.")
                if record['preferential'] is not None:
                    print(f"ID {record_id}: Preferential 칼럼이 이미 채워져 있습니다. 건너뜁니다.")

                # 값이 없는 경우만 업데이트
                updated_values = {
                    'responsibility': responsibility_text if record['responsibility'] is None else record['responsibility'],
                    'qualification': qualification_text if record['qualification'] is None else record['qualification'],
                    'preferential': preferential_text if record['preferential'] is None else record['preferential']
                }

                # 실제 업데이트가 필요한 경우만 실행
                if (
                    updated_values['responsibility'] != record['responsibility'] or
                    updated_values['qualification'] != record['qualification'] or
                    updated_values['preferential'] != record['preferential']
                ):
                    print(f"ID {record_id} 업데이트: {updated_values}")
                    update_database(
                        record_id,
                        updated_values['responsibility'],
                        updated_values['qualification'],
                        updated_values['preferential']
                    )
                else:
                    print(f"ID {record_id}: 업데이트할 항목이 없습니다. 건너뜁니다.")

        except Exception as e:
            print(f"레코드 처리 중 오류 발생: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    # 실행
    process_records()


def main():
    print(f"점핏 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    jumpit_txt()
    print(f"점핏 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    print(f"원티드 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    wanted_txt()
    print(f"원티드 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"인크루트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    incruit_txt()
    print(f"인크루트 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    print(f"로켓펀치 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rocketpunch_txt()
    print(f"로켓펀치 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    print(f"잡코리아 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    jobkorea_txt()
    print(f"잡코리아 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

    print(f"사람인 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    saramin_txt()
    print(f"사람인 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    time.sleep(10)

if __name__ == "__main__":
    main()
