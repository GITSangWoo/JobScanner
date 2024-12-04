import boto3
import mysql.connector
from mysql.connector import pooling
import datetime
import re

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
        responsibility_start_keywords = ["주요업무", "ㅣ 담당 업무", "[주요 업무]", "담당업무", "[주요업무]", "[담당업무]", "모집부문 : 데이터플랫폼 엔지니어", "[주요업무]", "설비혁신부문", " [담당업무]", "경력 소프트웨어 엔지니어 담당업무", "담당업무 Field Team 1명", "담당 업무", "2. 담당업무", "| 주요 업무", "주요 업무", "업무내용", "[담당업무 및 필요경험]", "(신입)", "[담당업무] ", "데이터 엔지니어", "담당업무", "이러한 업무를 수행합니다.", "데이터 플랫폼 엔지니어", "o 담당 업무", "       정비기술본부 주요업무   ", "Responsibilities", "QA팀(품질보증팀) 담당 업무", "기술 지원", "담당업무 (개발 직무 아님)", "모집부문 담당업무 자격요건 우대사항", " ※ 담당업무", " 이러한 업무를 수행합니다.", "*.Data Scientist는,", "시스템", "이런 업무를 해요 (주요 업무)", "이런 업무를 해요 (주요 업무) ", "수행업무", "근무지: 메가존산학연센터", "ㆍ기술 : Windows, Linux 서버 관리 기술", "| 합류하면 담당할 업무예요", "모집분야", "(신입/경력)", "[업무내용]", "\bDBA 영입", "✔ 이런 업무를 담당합니다", "[Responsibilities]", "엔지니어 [ 주요업무 ]", "근무지: 메가존산학연센터", "[담당 업무]", "[ 담당업무 ]", "[우리는 이런 일을 합니다]", "경력 3년 이상 15년이하", "▶ 담당업무", "담당업무 자격요건 및 우대사항", "  ■ 담당업무", "0명 모집 분야", "✔️ 이런 일을 합니다.", "Client Engineer (iOS/Android)", "SI 프로젝트)", "업무분야", "근무지: 역삼역 인근", "<담당업무>", "솔루션 엔지니어 (시스템 엔지니어) 사업2본부 1명", "| 합류하면 담당할 업무예요", "[이런 일을 합니다.]", "※ 입사하게 되면 함께 할 업무에요"]
        responsibility_end_keywords = ["지원자격", " ㅣ 지원자격", "[근무 조건]", "우대사항", "자격요건", "[자격요건]", "[지원자격]", "[필수자격]", "근무조건", "[근무지] 서울시 성동구", "자격 요건", " [자격요건]", "취급제품", "자격요건", "자격 요건", "3. 자격요건", "| 자격요건", "자격요건", "[우대사항]", "ㆍ클라우드 기반 시스템 관리 설계 및 운영 [필수 자격 조건]", "- BigQuery 등 데이터 웨어하우스 관련 경험", "자격요건", "이러한 역량과 경험이 있는 분들을 찾습니다.", "- 클라우드 환경 구축 경험", "자격 요건 ", "o 필요기술 및 우대사항(관련 경력)", "모집부문 상세내용", "Qualifications", "지원 자격요건", "- 관련 경력 3년 이상", "경력 3년 이상", "ㅣ자격사항", "* 이런 분이 필요해요!", "이런 분들을 찾고 있어요 (자격 요건)", " 이런 분들을 찾고 있어요 (자격 요건)", " | 이런 분과 함께 하고 싶어요", "자격 요건 0명", "자격요건 및 자격 (상세요건 및 우대사항)", "[필수조건]", "- 자격요건 - MySQL 운영 경험 있으신 분 (설치, 백업복구, HA, DR 등)", "✔ 이런 역량을 갖춘 분을 찾습니다", "[Requirements]", "[ 지원자격 ]", "[필요 자격]", "[ 우대사항 ]", "[우리는 이런 사람을 원합니다]", "[기술스택]", "3. 2개부문 공통 우대사항", "▶ 자격요건", "[ 자격요건 ]", "✔️ 이런 분을 찾고 있어요.", "[자격 요건]", "ㆍ 근무지역 : 대신파이낸스센터", "<우대사항>", " ㆍ요구사항", " | 이런 분과 함께 하고 싶어요", "[이런 분을 찾습니다.]", "※ 이런 분을 찾고 있어요"]
        # 자격 요건
        qualification_start_keywords = ["지원자격", " ㅣ 지원자격", "[자격 요건]", "자격요건", "[자격요건]", "[지원자격]", "-필수요건:", "[필수자격]", "지원자격", "공통 자격요건", "[지원자격]", "<지원자격>", "모집부문 담당업무 자격요건", "공통요건", " [자격요건]", "주요요건", "자격 요건", "3. 자격요건", "| 자격요건", "ㆍ클라우드 기반 시스템 관리 설계 및 운영 [필수 자격 조건]", "- 마케팅 솔루션에서 제공된 API로 데이터를 적재", "이러한 역량과 경험이 있는 분들을 찾습니다.", "- 데이터 플랫폼 구축 및 운영", "o 자격요건", "자격요건", "공통 자격요건 및", "Qualifications", "지원 자격요건", "   니어", "Teams, Microsoft Back Office 구축 및 기술 지원", "ㅣ자격사항", "* 이런 분이 필요해요!", "자격 요건", "이런 분들을 찾고 있어요 (자격 요건)", " 이런 분들을 찾고 있어요 (자격 요건)", " | 이런 분과 함께 하고 싶어요", "[필요기술]", "[필수조건]", "- 데이터 이관 및 마이그레이션", "✔ 이런 역량을 갖춘 분을 찾습니다", "필요역량", "[Requirements]", "[ 지원자격 ]", "필요역량", "[우리는 이런 사람을 원합니다]", "- 자격요건 및 우대사항", "▶ 자격요건", "[ 자격요건 ]", "■ 지원자격", "✔️ 이런 분을 찾고 있어요.", "[필요 역량 및 직무 경험]", "<지원자격>", " ㆍ요구사항", " | 이런 분과 함께 하고 싶어요", "[이런 분을 찾습니다.]", "※ 이런 분을 찾고 있어요"]
        qualification_end_keywords = ["우대사항", " [ 우대 사항 ]", "[우대 사항]", "담당업무", "[우대사항]", "[우대조건] ", "-기간:", "[우대사항]", "근무지역", "주요업무", "근무조건", "<근무지> 판교", "근무조건", "우대요건", " [우대사항]", "근무지: 경기도", "우대 사항", "4. 팀 구성", "| 우대 사항", " 우대요건", "- 관련 자격증 보유하신 분 (Cloud, RDB, SQL, Bigdata, IT 개발 관련)", "우대사항 ㆍGA(구글 애널리틱스), GTM(구글 태그매니저) 사용 경험", "이러한 강점이 있다면 더욱 좋습니다.", "- Crawling 개발 및 운영 경험 (IP / 로봇 차단 우회 경험)", "o 담당 업무", "우대조건", "- 하드웨어 개발", "※ 근무지 : 서울", "이런 분이면 더 좋아요", "- Microsoft 관련 기술 자격증 보유자", "Microsoft O365 / M365 유경험자", "ㅣ근무조건", "* 이런 경험이 있으면 더 좋아요!", "우대 조건", "이런 분이면 더 좋아요 (우대 사항)", " | 이런 분이면 더 좋아요", "근무조건", "[우대조건]", "- 우대사항 - 데이터 표준화 관리 경험이 있으신 분", "✔ 이런 역량이 있으면 더욱 좋습니다", "[Preferred Qualifications]", "필수 제출사항", "[우대요건]", "[ 우대사항 ]", "2.. 시스템엔지니어", "▶ 우대사항", "[ 우대사항 ]", "  ■ 우대사항", "✔️ 이런 분이면 더 좋아요.", "  ㆍ우대사항", " | 이런 분이면 더 좋아요", "[이런 경험이 있다면 더욱 좋습니다.]", "※ 이런 분이면 더 좋아요"]
        # 우대 사항
        preferential_start_keywords =["우대사항", " [ 우대 사항 ]", "[우대 사항]", "[우대사항]", "[우대조건] ", "[우대사항]", "우대요건", " [우대사항]", "우대 사항", "| 우대 사항", "우대요건", "- 관련 자격증 보유하신 분 (Cloud, RDB, SQL, Bigdata, IT 개발 관련)", "ㆍ자바스크립트 / 리눅스 사용 및 개발 경험자", "- SQL 중급 이상", "o 필요기술 및 우대사항(관련 경력)", "우대조건", "이런 분이면 더 좋아요", "   지식이 있는 분", "Microsoft 365 구축 또는 기술지원 가능자", "* 이런 경험이 있으면 더 좋아요!", "우대 조건", "이런 분이면 더 좋아요 (우대 사항)", " | 이런 분이면 더 좋아요", "[우대조건]", "- Docker 및 k8s 환경이 익숙하신 분", "✔ 이런 역량이 있으면 더욱 좋습니다", "[Preferred Qualifications]", "[우대요건]", "[ 우대사항 ]", "3. 2개부문 공통 우대사항", "▶ 우대사항", "[ 우대사항 ]", "이러한 강점이 있다면 더욱 좋습니다.", "  ■ 우대사항", "✔️ 이런 분이면 더 좋아요.", "<우대사항>", "  ㆍ우대사항", "있으면 좋은 우대사항 (우대사항은 보유하지 않아도 지원 가능합니다.)", " | 이런 분이면 더 좋아요", "[이런 경험이 있다면 더욱 좋습니다.]", "※ 이런 분이면 더 좋아요"]
        preferential_end_keywords = ["근무조건", "경력과 매칭되시는 분은", "함께하기 위한 방법", "근무조건", "마감일 및 근무지", "업무 상세", "[근무지]", "[복리후생]", "02. 급여 및 근무조건", "복지 및 혜택", "주요업무", "[주요업무]", "■ 급 여", "근무환경", "  [근무지]", "[복리후생]", "| 기타 사항", "혜택", "전형 절차", "함께하기 위한 방법", "(성수)&", "접수방법 - 사람인 온라인 입사지원", "※ 장애인은 관련 법령에 의하여 채용시 우대합니다", "근무지 ㆍ본사(성수)&프로젝트 파견지", "데이터 엔지니어", "회사사진  ", "혜택 및 복지", "- 하드웨어 개발", "함께하면 받는 혜택 및 복지", "복리후생", "근무형태 : 정규직 (수습기간 3개월)", "*.Data Platform Engineer에 지원하고 싶다면 아래의 서류를 제출해 주세요.", "ㆍETL 업무 수행 경험", "[꼭 읽어 주세요!]", "접수 및 절차", "지원서는 이렇게 작성하시면 좋아요", "전형안내", "※근무지 주소: 경기도 과천시 과천대로7길 74(갈현동, 메가존산학연센터)", " | 이렇게 합류해요", "사용 기술", "- 접수방법 온라인 공고 입사지원", "✔ 아래 여정을 통해 합류합니다", "함께하기 위한 방법", "근무조건 및 환경", "       근무조건", "※근무지 주소: 경기도 과천시 과천대로7길 74(갈현동, 메가존산학연센터)", "사용기술", "  근무조건", "- 호스팅 업체 근무 경험자", "근무조건은 확인해주세요", "ㆍRDB의 활용 경험과 SQL 작성이 가능하신분", "[근무조건]", "4. 이런분들은 지원하지 마세요 정중하게 거절합니다", "ㆍHW(서버,네트워크) 관련 일반 지식 보유자", "- Python, Shell 등으로 담당업무 개선 또는 자동화 경험 있으신 분", "채용 정보는 아래와 같습니다.", "- 비즈니스 문서 작성 및 발표(Presentation) 능력 우수자", "8) 운전가능하신 분 서울 대방", "  ■ 담당업무", "✔️ 이런 분이면 더 좋아요.", "[채용 전형 안내]", "기타사항", "근무지: 역삼역 인근", "<지원자격>", "접수기간 및 방법", "지원 시 참고사항", "업무환경", " | 이렇게 합류해요", "[이러한 일정으로 진행됩니다.]", "※ 함께하면 받는 혜택 및 복지"]

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
