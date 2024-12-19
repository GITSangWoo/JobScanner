import mysql.connector
from mysql.connector import Error

# RDS MySQL 연결 정보
host = 't2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com'
port = 3306
user = 'admin'
password = 'dltkddn1'
database = 'service'

# 각 기술에 대한 간단한 설명 (tech_description)
tech_descriptions = {
    "Jupyter": "Jupyter는 데이터 과학과 분석 작업을 위한 웹 기반 노트북 환경으로, 코드와 문서를 혼합하여 실행할 수 있습니다.",
    "Spyder": "Spyder는 파이썬 데이터 과학 환경을 위한 IDE로, 변수 탐색 및 강력한 디버깅 기능을 제공합니다.",
    "PyCharm": "PyCharm은 파이썬 개발을 위한 통합 개발 환경(IDE)으로, 코드 완성, 디버깅, 테스트 기능을 제공합니다.",
    "VSCode": "VSCode는 마이크로소프트에서 개발한 가벼운 코드 편집기로, 다양한 언어를 지원하고 확장성이 뛰어납니다.",
    "Sublime Text": "Sublime Text는 빠르고 유연한 텍스트 편집기로, 프로그래밍을 위한 기능을 제공합니다.",
    "Vim": "Vim은 효율적인 텍스트 편집기를 지향하는 명령 기반의 편집기입니다.",
    "Emacs": "Emacs는 사용자 정의가 가능한 텍스트 편집기이자 개발 환경으로, 확장성이 뛰어납니다.",
    "CI/CD": "CI/CD는 지속적인 통합(Continuous Integration)과 지속적인 배포(Continuous Deployment)로 소프트웨어 개발과 배포를 자동화하는 방법입니다.",
    "Machine Learning": "Machine Learning은 컴퓨터가 데이터를 통해 학습하고 예측을 수행하는 인공지능의 한 분야입니다.",
    "Deep Learning": "Deep Learning은 다층 신경망을 사용하여 복잡한 데이터에서 높은 수준의 추상화를 학습하는 머신러닝의 하위 분야입니다.",
    "Natural Language Processing": "Natural Language Processing(NLP)는 컴퓨터가 인간 언어를 이해하고 처리할 수 있도록 하는 기술입니다.",
    "Hadoop": "Hadoop은 대규모 데이터 저장과 처리를 위한 오픈 소스 프레임워크입니다.",
    "Spark": "Spark는 대규모 데이터 처리를 위한 빠르고 범용적인 분산 컴퓨팅 시스템입니다.",
    "Kafka": "Kafka는 대용량의 실시간 데이터 스트리밍을 처리하기 위한 분산 메시징 시스템입니다.",
    "HBase": "HBase는 분산형 NoSQL 데이터베이스로, Hadoop과 함께 대규모 데이터를 저장하고 처리합니다.",
    "Cassandra": "Cassandra는 대규모 데이터를 처리할 수 있는 고가용성 NoSQL 데이터베이스입니다.",
    "PostgreSQL": "PostgreSQL은 객체-관계형 데이터베이스 시스템으로, SQL 표준을 지원합니다.",
    "MySQL": "MySQL은 관계형 데이터베이스 관리 시스템(RDBMS)으로, 빠르고 신뢰성이 높습니다.",
    "SQLite": "SQLite는 경량화된 서버리스 관계형 데이터베이스 엔진입니다.",
    "MongoDB": "MongoDB는 NoSQL 데이터베이스로, JSON과 같은 문서 형식으로 데이터를 저장합니다.",
    "Redis": "Redis는 메모리 기반의 고속 키-값 데이터 저장소입니다.",
    "Elasticsearch": "Elasticsearch는 분산형 검색 엔진으로, 대규모 데이터에서 빠른 검색을 제공합니다.",
    "Solr": "Solr는 오픈 소스 검색 플랫폼으로, Apache Lucene을 기반으로 구축되었습니다.",
    "Apache Storm": "Apache Storm은 실시간 분산 스트리밍 데이터 처리 시스템입니다.",
    "Flume": "Flume은 대규모 로그 데이터를 수집, 집계 및 이동하는 분산 시스템입니다.",
    "Airflow": "Apache Airflow는 워크플로우 스케줄링 및 모니터링을 위한 플랫폼입니다.",
    "Celery": "Celery는 분산 작업 큐 시스템으로, 비동기 작업을 처리하는 데 사용됩니다.",
    "Apache Camel": "Apache Camel은 다양한 시스템 간 메시지 라우팅 및 변환을 처리하는 오픈 소스 통합 프레임워크입니다.",
    "Kotlin": "Kotlin은 자바와 호환되는 최신 프로그래밍 언어로, 안드로이드 앱 개발에 많이 사용됩니다.",
    "Java": "Java는 객체 지향적이며 플랫폼 독립적인 프로그래밍 언어로, 엔터프라이즈 애플리케이션 개발에 널리 사용됩니다.",
    "JavaScript": "JavaScript는 웹 개발에 널리 사용되는 클라이언트 사이드 스크립팅 언어입니다.",
    "TypeScript": "TypeScript는 JavaScript의 상위 집합으로, 정적 타입 시스템을 지원하는 프로그래밍 언어입니다.",
    "Swift": "Swift는 Apple에서 개발한 프로그래밍 언어로, iOS, macOS, watchOS, tvOS 앱 개발에 사용됩니다.",
    "Ruby": "Ruby는 간결하고 읽기 쉬운 문법을 가진 동적 객체 지향 프로그래밍 언어입니다.",
    "Go": "Go는 Google에서 개발한 프로그래밍 언어로, 병렬 처리 및 네트워크 서비스에 강점을 가집니다.",
    "Rust": "Rust는 메모리 안전성을 보장하는 시스템 프로그래밍 언어입니다.",
    "PHP": "PHP는 서버 사이드 웹 개발을 위한 스크립팅 언어로, 데이터베이스와 연동이 용이합니다.",
    "SQLAlchemy": "SQLAlchemy는 Python에서 관계형 데이터베이스와 상호작용하기 위한 라이브러리입니다.",
    "JDBC": "JDBC는 자바에서 관계형 데이터베이스와 연결하고 쿼리를 실행하는 API입니다.",
    "Selenium": "Selenium은 웹 애플리케이션 테스트를 자동화하는 도구로, 브라우저에서 사용자 상호작용을 시뮬레이션합니다.",
    "Cypress": "Cypress는 웹 애플리케이션의 엔드 투 엔드 테스트를 위한 JavaScript 기반의 자동화 도구입니다.",
    "Appium": "Appium은 모바일 애플리케이션의 자동화 테스트를 위한 오픈 소스 프레임워크입니다.",
    "Terraform": "Terraform은 인프라를 코드로 관리할 수 있는 도구로, 클라우드 인프라를 선언적으로 관리합니다.",
    "Ansible": "Ansible은 IT 자동화 도구로, 서버 구성, 애플리케이션 배포, 작업 자동화를 지원합니다.",
    "Docker": "Docker는 애플리케이션을 컨테이너화하여 일관된 환경에서 실행할 수 있도록 하는 플랫폼입니다.",
    "Kubernetes": "Kubernetes는 컨테이너화된 애플리케이션을 자동으로 배포하고 관리하는 오픈 소스 플랫폼입니다.",
    "OpenShift": "OpenShift는 Kubernetes 기반의 컨테이너 오케스트레이션 플랫폼으로, 기업 환경에 최적화되어 있습니다.",
    "Vagrant": "Vagrant는 가상화 환경을 자동으로 설정하고 관리하는 도구입니다.",
    "Git": "Git은 분산형 버전 관리 시스템으로, 코드 변경 이력을 추적하고 협업을 지원합니다.",
    "GitHub": "GitHub는 Git을 기반으로 한 코드 호스팅 플랫폼으로, 협업 및 버전 관리를 지원합니다.",
    "GitLab": "GitLab은 Git 저장소 관리, CI/CD, 코드 리뷰 등을 제공하는 DevOps 플랫폼입니다.",
    "Bitbucket": "Bitbucket은 Git과 Mercurial을 지원하는 Git 저장소 관리 플랫폼으로, 팀 협업 기능을 제공합니다.",
    "Jenkins": "Jenkins는 자동화 서버로, CI/CD 파이프라인을 구축하여 소프트웨어 개발 및 배포를 자동화합니다.",
    "Travis CI": "Travis CI는 GitHub와 통합되어 자동으로 빌드, 테스트, 배포하는 CI/CD 도구입니다.",
    "CircleCI": "CircleCI는 클라우드 기반의 CI/CD 플랫폼으로, 빠르고 확장 가능한 빌드, 테스트, 배포 환경을 제공합니다.",
    "Puppet": "Puppet은 시스템 및 애플리케이션의 자동화된 구성을 관리하는 오픈 소스 도구입니다.",
    "Chef": "Chef는 IT 인프라 자동화를 위한 구성 관리 도구로, 서버 설정과 애플리케이션 배포를 관리합니다.",
    "Nagios": "Nagios는 IT 인프라 모니터링 시스템으로, 서버와 네트워크 장비를 모니터링합니다.",
    "Prometheus": "Prometheus는 오픈 소스 시스템 모니터링 및 경고 도구로, 메트릭 수집 및 시계열 데이터 저장을 지원합니다.",
    "Grafana": "Grafana는 시각화 도구로, 다양한 데이터 소스에서 실시간 데이터를 시각화하고 대시보드를 제공합니다.",
    "Zabbix": "Zabbix는 IT 인프라 모니터링을 위한 오픈 소스 솔루션으로, 네트워크, 서버 및 애플리케이션을 모니터링합니다.",
    "Logstash": "Logstash는 로그 및 이벤트 데이터를 수집, 처리 및 저장하는 오픈 소스 도구입니다.",
    "Fluentd": "Fluentd는 로그 수집 및 처리를 위한 오픈 소스 데이터 수집기로, 다양한 형식의 로그를 처리합니다.",
    "Loggly": "Loggly는 클라우드 기반의 로그 관리 플랫폼으로, 실시간 로그 분석 및 모니터링을 지원합니다.",
    "Datadog": "Datadog은 클라우드 기반의 모니터링 플랫폼으로, 서버, 애플리케이션 및 로그 데이터를 실시간으로 모니터링합니다.",
    "New Relic": "New Relic은 애플리케이션 성능 모니터링(APM) 및 서버 모니터링 도구로, 실시간으로 시스템 상태를 추적합니다.",
    "Sentry": "Sentry는 애플리케이션 오류 추적 도구로, 오류 발생 시 실시간 알림을 제공하고 디버깅을 돕습니다.",
    "AppDynamics": "AppDynamics는 애플리케이션 성능 모니터링(APM) 도구로, 시스템 상태를 실시간으로 추적하고 분석합니다.",
    "GraphQL": "GraphQL은 클라이언트가 필요한 데이터를 정확히 요청할 수 있는 쿼리 언어이자 API 런타임입니다.",
    "REST API": "REST API는 HTTP를 기반으로 하는 웹 서비스 인터페이스로, 데이터 교환을 위해 널리 사용됩니다.",
    "gRPC": "gRPC는 구글에서 개발한 고성능 RPC 프레임워크로, 언어 독립적인 API 호출을 지원합니다.",
    "WebSocket": "WebSocket은 클라이언트와 서버 간의 양방향 통신을 지원하는 프로토콜입니다.",
    "Socket.io": "Socket.io는 실시간 웹 애플리케이션을 구축하기 위한 JavaScript 라이브러리로, WebSocket을 기반으로 합니다.",
    "Nginx": "Nginx는 고성능 웹 서버로, 리버스 프록시, 로드 밸런서, HTTP 캐싱 기능을 제공합니다.",
    "Apache HTTP Server": "Apache HTTP Server는 가장 널리 사용되는 웹 서버 소프트웨어로, 다양한 기능을 제공합니다.",
    "Lighttpd": "Lighttpd는 빠르고 효율적인 웹 서버로, 리소스가 제한된 환경에서 유용합니다.",
    "Tomcat": "Tomcat은 자바 서블릿 및 JSP를 실행하는 오픈 소스 웹 서버입니다.",
    "Jetty": "Jetty는 자바 기반의 HTTP 서버 및 서블릿 컨테이너로, 경량화된 웹 서버로 사용됩니다.",
    "WildFly": "WildFly는 자바 EE(Enterprise Edition) 애플리케이션 서버로, 자바 웹 애플리케이션을 배포하는 데 사용됩니다.",
    "Spring Boot": "Spring Boot는 자바 기반의 프레임워크로, 빠른 개발을 위해 설정을 최소화한 애플리케이션을 생성할 수 있습니다.",
    "Spring MVC": "Spring MVC는 모델-뷰-컨트롤러 패턴을 기반으로 한 웹 애플리케이션 프레임워크입니다.",
    "Spring Security": "Spring Security는 인증 및 권한 부여를 위한 자바 기반의 보안 프레임워크입니다.",
    "Spring Cloud": "Spring Cloud는 마이크로서비스 아키텍처를 구축하는 데 유용한 여러 프로젝트들을 제공하는 프레임워크입니다.",
    "Spring Data": "Spring Data는 데이터베이스와의 상호작용을 단순화하는 데이터 액세스 프레임워크입니다.",
    "Spring Batch": "Spring Batch는 대용량 데이터 처리 및 배치 작업을 위한 프레임워크입니다.",
    "Spring Integration": "Spring Integration은 엔터프라이즈 애플리케이션 통합을 위한 다양한 메시징 패턴을 제공합니다.",
    "Node.js": "Node.js는 서버 사이드에서 JavaScript를 실행할 수 있게 하는 런타임 환경입니다.",
    "Express": "Express는 Node.js 환경에서 웹 애플리케이션을 빠르게 개발할 수 있도록 도와주는 경량화된 프레임워크입니다.",
    "Vue.js": "Vue.js는 사용자 인터페이스 구축을 위한 자바스크립트 프레임워크로, 컴포넌트 기반 아키텍처를 지원합니다.",
    "React": "React는 사용자 인터페이스(UI)를 구축하기 위한 자바스크립트 라이브러리로, 상태 관리와 컴포넌트 렌더링을 효율적으로 처리합니다.",
    "Angular": "Angular는 구글에서 개발한 자바스크립트 기반의 프레임워크로, SPA(Single Page Application)를 구축하는 데 유용합니다.",
    "Svelte": "Svelte는 컴파일러 기반의 자바스크립트 프레임워크로, 빠르고 효율적인 웹 애플리케이션을 개발할 수 있습니다.",
    "Next.js": "Next.js는 React 기반의 프레임워크로, 서버 사이드 렌더링과 정적 사이트 생성 기능을 제공합니다.",
    "Nuxt.js": "Nuxt.js는 Vue.js 기반의 프레임워크로, 서버 사이드 렌더링 및 정적 사이트 생성을 지원합니다.",
    "Ember.js": "Ember.js는 자바스크립트 프레임워크로, 대규모 웹 애플리케이션을 구축할 수 있는 강력한 도구를 제공합니다.",
    "Django": "Django는 파이썬 기반의 웹 프레임워크로, 빠른 개발과 보안에 강점을 지니고 있습니다.",
    "Flask": "Flask는 파이썬 기반의 마이크로 웹 프레임워크로, 단순하고 유연한 웹 애플리케이션을 개발할 수 있습니다.",
    "Ruby on Rails": "Ruby on Rails는 루비 언어를 기반으로 하는 웹 애플리케이션 프레임워크로, 간단하고 빠른 개발을 지원합니다.",
    "Laravel": "Laravel은 PHP로 작성된 웹 애플리케이션 프레임워크로, 강력한 라우팅, 인증, 보안 기능을 제공합니다.",
    "Spring Framework": "Spring Framework는 자바 기반의 애플리케이션 프레임워크로, 의존성 주입 및 AOP를 지원합니다.",
    "ASP.NET": "ASP.NET은 마이크로소프트에서 개발한 웹 애플리케이션 프레임워크로, C#을 사용하여 강력한 웹 애플리케이션을 만듭니다.",
    "Symfony": "Symfony는 PHP 기반의 웹 애플리케이션 프레임워크로, 재사용 가능한 구성 요소를 제공합니다.",
    "Meteor": "Meteor는 풀 스택 자바스크립트 프레임워크로, 실시간 웹 애플리케이션을 쉽게 만들 수 있습니다.",
    "Hapi": "Hapi는 Node.js에서 사용하는 서버 프레임워크로, REST API 구축을 빠르고 간편하게 합니다.",
    "Golang": "Golang은 구글에서 개발한 시스템 프로그래밍 언어로, 높은 성능과 병행성을 지원합니다.",
    "C++": "C++는 시스템 프로그래밍, 게임 개발, 성능이 중요한 애플리케이션을 위한 고급 언어입니다.",
    "C#": "C#은 마이크로소프트에서 개발한 객체지향 프로그래밍 언어로, 주로 Windows 애플리케이션을 개발하는 데 사용됩니다.",
    "C": "C는 절차적 프로그래밍 언어로, 시스템 프로그래밍 및 성능이 중요한 애플리케이션 개발에 유용합니다.",
    "Python": "Python은 쉽고 직관적인 문법을 가진 고급 프로그래밍 언어로, 데이터 분석, 웹 개발, 자동화 등에 널리 사용됩니다.",
    "Perl": "Perl은 텍스트 처리 및 시스템 관리에 강점을 지닌 고급 프로그래밍 언어입니다.",
    "CoffeeScript": "CoffeeScript는 자바스크립트의 문법을 더 간결하게 작성할 수 있도록 돕는 언어입니다.",
    "Shell": "Shell은 운영 체제의 명령어를 실행하는 인터페이스로, 스크립트를 통해 자동화 작업을 처리합니다.",
    "SQL": "SQL(Structured Query Language)은 관계형 데이터베이스에서 데이터를 관리하고 질의하는 데 사용되는 언어입니다.",
    "NoSQL": "NoSQL은 비관계형 데이터베이스로, 대규모 분산 데이터베이스 시스템에서 유용합니다.",
    "MariaDB": "MariaDB는 MySQL의 포크로, 관계형 데이터베이스 관리 시스템(RDBMS)입니다. MySQL과 호환됩니다.",
    "Agit": "Agit은 팀 기반 소프트웨어 개발을 위해 설계된 협업 git 기반 도구로, 코드 리포지토리의 버전 관리 및 관리를 지원합니다.",
    "Tableau": "Tableau는 사용자에게 실시간 데이터 시각화 및 대시보드를 생성할 수 있는 인터랙티브한 데이터 시각화 도구입니다.",
    "PyTorch": "PyTorch는 딥 러닝 및 자연어 처리와 같은 애플리케이션에 사용되는 오픈 소스 머신러닝 라이브러리로, 신경망 구축을 위한 도구를 제공합니다.",
    "TensorFlow": "TensorFlow는 머신러닝, 특히 딥 러닝을 위한 오픈 소스 플랫폼으로, 모델 구축, 훈련 및 배포를 위한 도구를 제공합니다.",
    "AWS Athena": "AWS Athena는 표준 SQL을 사용하여 Amazon S3에 있는 데이터를 직접 분석할 수 있게 해주는 대화형 쿼리 서비스입니다.",
    "LLM": "LLM(대형 언어 모델)은 많은 수의 매개변수를 가진 인공지능 모델로, 인간과 유사한 텍스트를 이해하고 생성할 수 있습니다.",
    "CSS": "CSS(캐스케이딩 스타일 시트)는 웹 페이지의 레이아웃, 색상, 글꼴 등을 설명하는 스타일시트 언어입니다.",
    "Amazon S3": "Amazon S3(Simple Storage Service)는 데이터 백업, 아카이브 및 분석을 위한 확장 가능한 객체 저장소를 제공하며, 사용자는 클라우드에서 데이터를 저장하고 검색할 수 있습니다.",
    "AWS Redshift": "AWS Redshift는 복잡한 쿼리를 빠르고 비용 효율적으로 실행할 수 있게 해주는 관리형 클라우드 데이터 웨어하우스 서비스입니다.",
    "Firebase": "Firebase는 모바일 및 웹 애플리케이션 개발을 위한 플랫폼으로, 데이터베이스, 인증, 클라우드 메시징과 같은 다양한 도구를 제공합니다.",
    "Snowflake": "Snowflake는 데이터 저장, 처리 및 분석 솔루션을 제공하는 클라우드 기반 데이터 웨어하우징 플랫폼으로, 확장 가능하고 관리가 용이합니다.",
    "Amazon CloudWatch": "Amazon CloudWatch는 AWS 클라우드 리소스 및 애플리케이션의 모니터링 서비스로, 메트릭 및 로그에 대한 실시간 가시성을 제공합니다.",
    "Impala": "Impala는 Hadoop에 저장된 대규모 데이터를 빠르고 대화형으로 분석할 수 있게 해주는 오픈 소스 분산 SQL 쿼리 엔진입니다.",
    "GitHub Actions": "GitHub Actions는 GitHub 저장소의 워크플로 자동화를 위한 CI/CD 도구입니다."
}

# MySQL 연결
try:
    connection = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

    if connection.is_connected():
        print("MySQL 서버에 연결되었습니다.")

        # 커서 생성
        cursor = connection.cursor()

        # 각 기술에 대한 설명을 tech_stack 테이블에 업데이트하는 쿼리 준비
        update_query = """
        UPDATE tech_stack
        SET tech_description = %s
        WHERE tech_name = %s
        """

        # 기술 이름에 맞는 설명 업데이트
        for tech_name, tech_description in tech_descriptions.items():
            cursor.execute(update_query, (tech_description, tech_name))

        # 변경 사항 커밋
        connection.commit()
        print(f"{len(tech_descriptions)}개의 기술 스택 설명이 업데이트되었습니다.")

except Error as e:
    print(f"에러 발생: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL 연결이 종료되었습니다.")

