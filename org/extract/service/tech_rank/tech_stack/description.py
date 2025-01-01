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
    "Airflow": "Apache Airflow는 데이터 파이프라인을 작성, 스케줄링 및 모니터링하는 오픈소스 워크플로우 오케스트레이션 도구입니다.",
    "Amazon CloudWatch": "Amazon CloudWatch는 AWS 리소스와 애플리케이션의 모니터링 및 로그 관리를 제공하는 서비스입니다.",
    "Amazon DynamoDB": "Amazon DynamoDB는 AWS에서 제공하는 완전 관리형 NoSQL 데이터베이스로, 높은 확장성과 일관된 성능을 제공합니다.",
    "Amazon EC2": "Amazon EC2는 AWS 클라우드에서 확장 가능한 컴퓨팅 용량을 제공하는 가상 서버 서비스입니다.",
    "Amazon EKS": "Amazon EKS는 AWS에서 제공하는 완전 관리형 Kubernetes 서비스로, 클러스터의 가용성과 확장성을 자동으로 관리합니다.",
    "Amazon Lambda": "AWS Lambda는 이벤트 기반으로 코드를 실행하고 서버를 관리하지 않아도 되는 서버리스 컴퓨팅 서비스입니다.",
    "Amazon Neptune": "Amazon Neptune은 고성능 그래프 데이터베이스 서비스로, 관계형 데이터 분석과 같은 작업에 최적화되어 있습니다.",
    "Amazon RDS": "Amazon RDS는 AWS에서 제공하는 관리형 관계형 데이터베이스 서비스로, 다양한 데이터베이스 엔진을 지원합니다.",
    "Amazon S3": "Amazon S3는 확장 가능한 객체 스토리지 서비스로, 데이터를 안전하게 저장하고 검색할 수 있습니다.",
    "Amazon SNS": "Amazon SNS는 메시지 게시 및 구독을 지원하는 완전 관리형 메시징 서비스입니다.",
    "Amazon SQS": "Amazon SQS는 분산 메시지 대기열 서비스로, 애플리케이션 간 비동기 통신을 지원합니다.",
    "Amazon VPC": "Amazon VPC는 AWS 클라우드 내에서 격리된 네트워크를 생성할 수 있는 가상 네트워크 서비스입니다.",
    "Angular": "Angular는 Google에서 개발한 TypeScript 기반의 프론트엔드 웹 애플리케이션 프레임워크입니다.",
    "Ansible": "Ansible은 IT 자동화를 위한 오픈소스 도구로, 구성 관리 및 애플리케이션 배포를 지원합니다.",
    "Apache Camel": "Apache Camel은 다양한 시스템 간의 통합을 단순화하기 위한 오픈소스 통합 프레임워크입니다.",
    "Apache Cassandra": "Apache Cassandra는 분산형 NoSQL 데이터베이스로, 높은 가용성과 확장성을 제공합니다.",
    "Apache HTTP Server": "Apache HTTP Server는 오픈소스 웹 서버 소프트웨어로, HTTP 요청을 처리하고 웹 콘텐츠를 제공합니다.",
    "Apache Storm": "Apache Storm은 실시간 데이터 스트리밍 처리를 위한 분산형 컴퓨팅 시스템입니다.",
    "AppDynamics": "AppDynamics는 애플리케이션 성능 모니터링(APM) 도구로, 실시간 성능 데이터를 제공합니다.",
    "Appium": "Appium은 모바일 애플리케이션 테스트를 자동화하기 위한 오픈소스 도구입니다.",
    "ArangoDB": "ArangoDB는 멀티모델 데이터베이스로, 그래프, 문서 및 키-값 데이터를 지원합니다.",
    "ASP.NET": "ASP.NET은 Microsoft에서 개발한 웹 애플리케이션 프레임워크로, 동적 웹 페이지를 생성할 수 있습니다.",
    "AWS Athena": "AWS Athena는 SQL 쿼리를 사용하여 Amazon S3에 저장된 데이터를 분석할 수 있는 서버리스 쿼리 서비스입니다.",
    "AWS Redshift": "AWS Redshift는 대규모 데이터 분석 작업에 최적화된 완전 관리형 데이터 웨어하우스 서비스입니다.",
    "Berkeley DB": "Berkeley DB는 임베디드 키-값 데이터베이스 라이브러리로, 고성능 트랜잭션 처리를 지원합니다.",
    "Bitbucket": "Bitbucket은 소프트웨어 개발 팀을 위한 Git 기반 코드 저장소 및 협업 플랫폼입니다.",
    "C": "\"C\" 언어는 시스템 소프트웨어와 응용 프로그램 개발에 널리 사용되는 범용 프로그래밍 언어입니다.",
    "C#": "\"C#\"은 Microsoft에서 개발한 객체 지향 프로그래밍 언어로, .NET 플랫폼에서 실행됩니다.",
    "C++": "\"C++\"은 고성능 응용 프로그램과 시스템 소프트웨어 개발에 사용되는 객체 지향 프로그래밍 언어입니다.",
    "Cassandra": "Cassandra는 Apache에서 개발한 분산형 NoSQL 데이터베이스로, 높은 가용성과 확장성을 제공하며 대규모 데이터 처리에 최적화되어 있습니다.",
    "Celery": "Celery는 Python 기반의 비동기 태스크 큐로, 분산 작업 처리를 지원하며 작업 스케줄링과 큐 관리에 유용합니다.",
    "Chef": "Chef는 IT 자동화를 위한 구성 관리 도구로, 인프라를 코드로 정의하고 서버 설정을 자동화합니다.",
    "CircleCI": "CircleCI는 CI/CD(지속적 통합 및 배포)를 지원하는 클라우드 기반 플랫폼으로, 소프트웨어 빌드, 테스트 및 배포를 자동화합니다.",
    "CoffeeScript": "CoffeeScript는 JavaScript로 컴파일되는 프로그래밍 언어로, 간결하고 읽기 쉬운 문법을 제공합니다.",
    "CSS": "CSS(Cascading Style Sheets)는 웹 페이지의 디자인과 레이아웃을 정의하는 스타일링 언어입니다.",
    "Cypress": "Cypress는 현대 웹 애플리케이션의 엔드 투 엔드 테스트를 자동화하기 위한 JavaScript 기반 테스트 프레임워크입니다.",
    "Datadog": "Datadog은 클라우드 기반 모니터링 및 분석 플랫폼으로, IT 인프라와 애플리케이션의 실시간 성능 데이터를 제공합니다.",
    "Deep Learning": "Deep Learning은 인공 신경망을 사용하여 데이터를 학습하는 머신 러닝의 하위 분야로, 이미지 인식 및 자연어 처리 등에 활용됩니다.",
    "Django": "Django는 Python 기반의 웹 프레임워크로, 빠르고 효율적인 웹 애플리케이션 개발을 지원하며 DRY 원칙을 따릅니다.",
    "Docker": "Docker는 컨테이너 기술을 사용하여 애플리케이션을 패키징, 배포 및 실행할 수 있는 오픈소스 플랫폼입니다.",
    "Elasticsearch": "Elasticsearch는 Apache Lucene 기반의 분산형 검색 및 분석 엔진으로, 대규모 데이터의 빠른 검색과 분석을 지원합니다.",
    "Emacs": "Emacs는 GNU 프로젝트에서 개발된 확장 가능한 텍스트 편집기로, Emacs Lisp를 통해 사용자 정의가 가능합니다.",
    "Ember.js": "Ember.js는 JavaScript 기반의 오픈소스 웹 프레임워크로, MVC 패턴을 사용하여 대규모 클라이언트 애플리케이션 개발에 적합합니다.",
    "Express": "Express는 Node.js를 위한 경량 웹 애플리케이션 프레임워크로, 빠르고 유연한 서버 구축을 지원합니다.",
    "FastAPI": "FastAPI는 Python으로 작성된 고성능 API 개발 프레임워크로, 간단하고 직관적인 문법과 OpenAPI 지원을 제공합니다.",
    "Firebase": "Firebase는 Google에서 제공하는 백엔드 서비스 플랫폼으로, 실시간 데이터베이스와 인증 기능 등을 제공합니다.",
    "Flask": "Flask는 Python으로 작성된 경량 웹 프레임워크로, 간단하고 확장 가능한 웹 애플리케이션 개발에 적합합니다.",
    "Fluentd": "Fluentd는 로그 데이터를 수집하고 변환하여 다양한 데이터 저장소로 전송할 수 있는 오픈소스 데이터 수집 도구입니다.",
    "Flume": "Apache Flume은 대규모 로그 데이터를 효율적으로 수집하고 전송하기 위한 분산형 데이터 수집 시스템입니다.",
    "Git": "Git은 분산 버전 관리 시스템으로, 소스 코드 관리와 협업을 용이하게 합니다.",
    "GitHub": "GitHub는 Git 저장소 호스팅 서비스로, 코드 공유와 협업 도구를 제공합니다.",
    "GitHub Actions": "GitHub Actions는 GitHub에서 제공하는 CI/CD 워크플로우 자동화 도구입니다.",
    "GitLab": "GitLab은 Git 기반 저장소 관리와 CI/CD 파이프라인을 통합적으로 제공하는 DevOps 플랫폼입니다.",
    "GO": "\"GO\" 또는 \"Golang\"은 Google에서 개발한 고성능 프로그래밍 언어로, 간결성과 병렬 처리를 강조합니다.",
    "Grafana": "Grafana는 모니터링 데이터를 시각화하고 대시보드를 생성할 수 있는 오픈소스 도구입니다.",
    "GraphQL": "GraphQL은 Facebook에서 개발한 데이터 쿼리 언어로, API 요청 시 필요한 데이터만 선택적으로 가져올 수 있습니다.",
    "gRPC": "gRPC는 Google에서 개발한 원격 프로시저 호출(RPC) 프레임워크로, 고성능 마이크로서비스 통신에 사용됩니다.",
    "Hadoop": "Hadoop은 대규모 데이터를 분산 처리하기 위한 오픈소스 프레임워크로, HDFS와 MapReduce를 포함합니다.",
    "Hapi": "Hapi는 Node.js 기반의 오픈소스 웹 프레임워크로, 서버, 웹사이트 및 HTTP 프록시 애플리케이션 개발을 지원하며, 인증 및 캐싱 기능을 내장하고 있습니다.",
    "HBase": "HBase는 Apache Hadoop 위에서 실행되는 컬럼 지향 비관계형 데이터베이스로, 대규모의 희소 데이터 세트를 실시간으로 처리할 수 있도록 설계되었습니다.",
    "Helm": "Helm은 Kubernetes 애플리케이션을 위한 패키지 관리 도구로, 애플리케이션 배포, 업그레이드 및 관리를 자동화합니다.",
    "Hypertable": "Hypertable은 Google의 Bigtable을 모델로 한 오픈소스 분산 데이터베이스로, 대규모 데이터를 빠르게 처리할 수 있도록 설계되었습니다.",
    "Impala": "Impala는 Apache Hadoop 기반의 분산 SQL 엔진으로, 대규모 데이터에 대해 실시간 쿼리를 실행할 수 있습니다.",
    "Java": "Java는 객체 지향 프로그래밍 언어로, 플랫폼 독립성을 제공하며 다양한 애플리케이션 개발에 사용됩니다.",
    "JavaScript": "JavaScript는 웹 개발에서 HTML 및 CSS와 함께 사용되는 프로그래밍 언어로, 클라이언트와 서버 측 애플리케이션 개발에 활용됩니다.",
    "JDBC": "JDBC(Java Database Connectivity)는 Java 애플리케이션이 데이터베이스에 연결하고 SQL 쿼리를 실행할 수 있도록 지원하는 API입니다.",
    "Jenkins": "Jenkins는 지속적 통합 및 지속적 배포(CI/CD)를 지원하는 오픈소스 자동화 서버로, 소프트웨어 빌드, 테스트 및 배포를 자동화합니다.",
    "Jetty": "Jetty는 경량의 Java 기반 웹 서버 및 서블릿 컨테이너로, 임베디드 서버 환경에서 자주 사용됩니다.",
    "Jupyter": "Jupyter는 데이터 과학과 분석 작업을 위한 웹 기반 노트북 환경으로, 코드와 문서를 혼합하여 실행할 수 있습니다.",
    "Kafka": "Apache Kafka는 분산 스트리밍 플랫폼으로, 실시간 데이터 스트림 처리와 데이터 파이프라인 구축에 사용됩니다.",
    "Kotlin": "Kotlin은 Google에서 공식적으로 지원하는 정적 타입의 프로그래밍 언어로, 객체 지향 및 함수형 프로그래밍을 지원하며 주로 Android 개발에 사용됩니다.",
    "Kubernetes": "Kubernetes는 컨테이너화된 애플리케이션의 배포, 확장 및 관리를 자동화하는 오픈소스 컨테이너 오케스트레이션 시스템입니다.",
    "Laravel": "Laravel은 PHP 기반의 오픈소스 웹 프레임워크로, MVC 아키텍처를 따르며 현대적인 웹 애플리케이션 개발을 지원합니다.",
    "Lighttpd": "Lighttpd는 고성능 환경에 최적화된 경량 웹 서버로, 낮은 메모리 사용량과 높은 CPU 효율성을 제공합니다.",
    "LLM": "LLM(Large Language Model)은 인간 언어를 처리하고 생성하는 데 특화된 인공지능(AI) 모델로, 자연어 처리 작업에 주로 사용됩니다.",
    "Loggly": "Loggly는 클라우드 기반 로그 관리 도구로, 로그 데이터를 수집하고 분석하여 문제를 빠르게 식별하고 해결할 수 있도록 돕습니다.",
    "Logstash": "Logstash는 데이터를 수집하고 변환하여 다양한 목적지로 전송할 수 있는 오픈소스 데이터 처리 파이프라인 도구입니다.",
    "Machine Learning": "Machine Learning(기계 학습)은 데이터를 학습하여 패턴을 인식하고 예측을 수행하는 인공지능(AI)의 하위 분야입니다.",
    "MariaDB": "MariaDB는 MySQL에서 포크된 오픈소스 관계형 데이터베이스 관리 시스템으로, 높은 성능과 안정성을 제공합니다.",
    "Meteor": "Meteor는 JavaScript 기반의 풀스택 웹 프레임워크로, 클라이언트와 서버 간 실시간 데이터 동기화를 지원합니다.",
    "MongoDB": "MongoDB는 문서 지향 NoSQL 데이터베이스로, JSON과 유사한 형식으로 데이터를 저장하며 유연성과 확장성을 제공합니다.",
    "MySQL": "MySQL은 오픈소스 관계형 데이터베이스 관리 시스템으로, 다양한 애플리케이션에서 널리 사용됩니다.",
    "Nagios": "Nagios는 IT 인프라 모니터링 도구로, 서버와 네트워크 장치의 상태를 실시간으로 확인할 수 있습니다.",
    "Natural Language Processing": "NLP(자연어 처리)는 인간 언어를 이해하고 처리하기 위한 인공지능 기술입니다.",
    "Neo4j": "Neo4j는 그래프 데이터베이스로, 노드와 관계를 통해 데이터를 저장하고 쿼리합니다.",
    "New Relic": "New Relic은 애플리케이션 성능 모니터링(APM) 도구로, 실시간 성능 데이터를 제공하여 문제를 신속히 해결할 수 있도록 돕습니다.",
    "Next.js": "Next.js는 React 기반의 프레임워크로, 서버 사이드 렌더링과 정적 사이트 생성 기능을 제공합니다.",
    "Nginx": "Nginx는 고성능 웹 서버 및 리버스 프록시 서버로, 정적 콘텐츠 제공과 로드 밸런싱을 지원합니다.",
    "Node.js": "Node.js는 JavaScript를 기반으로 한 오픈소스 서버 환경으로, 비동기 이벤트 기반 구조를 통해 높은 확장성과 성능을 제공합니다.",
    "NoSQL": "NoSQL은 관계형 데이터베이스가 아닌 다양한 데이터 모델(문서, 그래프, 키-값 등)을 지원하며, 유연성과 확장성을 강조하는 데이터베이스 유형입니다.",
    "Nuxt.js": "Nuxt.js는 Vue.js 기반의 프레임워크로, 서버 사이드 렌더링(SSR) 및 정적 사이트 생성을 지원하여 SEO와 성능을 개선합니다.",
    "OpenShift": "OpenShift는 Red Hat에서 제공하는 Kubernetes 기반의 하이브리드 클라우드 플랫폼으로, 애플리케이션 배포 및 관리를 자동화합니다.",
    "Oracle": "Oracle Database는 고성능과 안정성을 제공하는 상용 관계형 데이터베이스 관리 시스템으로, 대규모 엔터프라이즈 환경에 적합합니다.",
    "OrientDB": "OrientDB는 그래프, 문서, 키-값 및 객체 지향 저장소를 지원하는 멀티모델 NoSQL 데이터베이스입니다.",
    "Perl": "Perl은 텍스트 처리와 시스템 관리 작업에 널리 사용되는 고수준의 동적 스크립팅 언어입니다.",
    "PHP": "PHP는 서버 사이드 스크립팅 언어로, 동적 웹 페이지와 애플리케이션 개발에 널리 사용됩니다.",
    "PostgreSQL": "PostgreSQL는 SQL과 JSON 쿼리를 지원하는 오픈소스 객체 관계형 데이터베이스로, 안정성과 확장성이 뛰어납니다.",
    "Prometheus": "Prometheus는 메트릭 수집 및 모니터링을 위한 오픈소스 시스템으로, 경고 기능과 시계열 데이터 저장소를 제공합니다.",
    "Puppet": "Puppet은 IT 인프라 구성 관리 및 자동화를 지원하는 오픈소스 도구로, 코드로 인프라를 정의할 수 있습니다.",
    "PyCharm": "PyCharm은 Python 개발을 위한 통합 개발 환경(IDE)으로, 코드 완성 및 디버깅 기능을 제공합니다.",
    "Python": "Python은 간결하고 읽기 쉬운 문법을 가진 고수준 프로그래밍 언어로, 다양한 응용 프로그램 개발에 사용됩니다.",
    "PyTorch": "PyTorch는 동적 계산 그래프를 사용하는 딥러닝 프레임워크로, GPU 가속과 유연한 신경망 설계를 지원합니다.",
    "React": "React는 컴포넌트 기반의 사용자 인터페이스(UI) 라이브러리로, 효율적인 DOM 업데이트를 통해 성능을 최적화합니다.",
    "Redash": "Redash는 데이터를 시각화하고 대시보드를 생성하여 팀 간 협업을 지원하는 데이터 분석 도구입니다.",
    "Redis": "Redis는 인메모리 키-값 데이터베이스로, 캐싱 및 메시지 브로커 역할을 수행하며 높은 성능을 제공합니다.",
    "REST API": "REST API는 HTTP 프로토콜을 기반으로 자원을 CRUD 방식으로 처리하는 아키텍처 스타일입니다.",
    "Riak": "Riak은 분산형 NoSQL 데이터베이스로, 높은 가용성과 확장성을 제공합니다.",
    "Ruby": "Ruby는 간결하고 생산성을 중시하는 객체 지향 프로그래밍 언어로, 웹 애플리케이션 개발에 자주 사용됩니다.",
    "Ruby on Rails": "Ruby on Rails는 Ruby 기반의 웹 애플리케이션 프레임워크로, MVC 아키텍처를 따릅니다.",
    "Rust": "Rust는 메모리 안전성과 병렬 처리를 강조한 시스템 프로그래밍 언어입니다.",
    "ScyllaDB": "ScyllaDB는 Apache Cassandra와 호환되는 고성능 NoSQL 데이터베이스입니다.",
    "Selenium": "Selenium은 웹 애플리케이션 테스트 자동화를 위한 오픈소스 도구입니다.",
    "Sentry": "Sentry는 애플리케이션 오류 추적 및 성능 모니터링 도구로, 문제를 빠르게 식별하고 해결할 수 있도록 돕습니다.",
    "Shell": "Shell은 명령줄 인터페이스(CLI)에서 명령을 실행하고 스크립트를 작성할 수 있는 인터프리터입니다.",
    "Snowflake": "Snowflake는 클라우드 기반의 데이터 웨어하우스로, 대규모 데이터를 효율적으로 처리하고 분석할 수 있습니다.",
    "Socket.io": "Socket.io는 실시간 양방향 통신을 지원하는 JavaScript 라이브러리로, WebSocket 프로토콜 위에서 동작합니다.",
    "Solr": "Solr는 Apache Lucene 기반의 오픈소스 검색 플랫폼으로, 대규모 텍스트 검색과 분석을 지원합니다.",
    "Spark": "Apache Spark는 대규모 데이터를 빠르게 처리하기 위한 분산형 데이터 처리 엔진입니다.",
    "Spring Batch": "Spring Batch는 대량의 데이터 처리를 위한 배치 애플리케이션 프레임워크로, 데이터 읽기, 처리, 쓰기 작업을 표준화하고 효율적으로 관리합니다.",
    "Spring Boot": "Spring Boot는 Spring Framework를 기반으로 한 확장 도구로, 최소한의 설정으로 독립 실행형 애플리케이션을 빠르게 개발할 수 있도록 지원합니다.",
    "Spring Cloud": "Spring Cloud는 마이크로서비스 개발을 위한 도구와 기술을 제공하며, 서비스 등록, 로드 밸런싱, 라우팅 등의 기능을 지원합니다.",
    "Spring Data": "Spring Data는 다양한 데이터 저장소와의 통합을 단순화하여 데이터 접근 계층을 쉽게 구현할 수 있도록 지원하는 프로젝트입니다.",
    "Spring Framework": "Spring Framework는 Java 애플리케이션 개발을 위한 포괄적인 인프라를 제공하며, 의존성 주입과 AOP 같은 기능을 지원합니다.",
    "Spring Integration": "Spring Integration은 엔터프라이즈 통합 패턴(EIP)을 지원하며, 메시지 기반 애플리케이션 개발을 단순화합니다.",
    "Spring MVC": "Spring MVC는 모델-뷰-컨트롤러(MVC) 아키텍처를 기반으로 웹 애플리케이션 개발을 지원하는 Spring Framework의 모듈입니다.",
    "Spring Security": "Spring Security는 인증 및 권한 부여를 포함한 보안 기능을 제공하며, 웹 애플리케이션과 독립 실행형 애플리케이션에서 사용됩니다.",
    "Spyder": "Spyder는 Python 프로그래밍 언어를 위한 과학 계산 환경으로, 코드 편집기와 디버거를 포함한 다양한 도구를 제공합니다.",
    "SQL": "SQL(Structured Query Language)은 관계형 데이터베이스에서 데이터를 정의하고 조작하기 위한 표준 언어입니다.",
    "SQLAlchemy": "SQLAlchemy는 Python용 SQL 툴킷 및 ORM(Object Relational Mapper)으로, 데이터베이스와의 상호작용을 단순화합니다.",
    "SQLite": "SQLite는 서버리스, 자체 포함형 SQL 데이터베이스 엔진으로, 경량성과 높은 신뢰성을 제공합니다.",
    "Sublime Text": "Sublime Text는 빠르고 가벼운 코드 편집기로, 다양한 프로그래밍 언어에 대한 구문 강조 및 플러그인 지원을 제공합니다.",
    "Svelte": "Svelte는 컴파일 단계에서 UI 코드를 최적화하여 빠르고 효율적인 웹 애플리케이션을 개발할 수 있는 프론트엔드 프레임워크입니다.",
    "Swift": "Swift는 Apple에서 개발한 프로그래밍 언어로, iOS 및 macOS 애플리케이션 개발에 주로 사용됩니다.",
    "Symfony": "Symfony는 PHP 기반의 웹 애플리케이션 프레임워크로, 재사용 가능한 컴포넌트를 통해 빠르고 효율적인 개발을 지원합니다.",
    "Tableau": "Tableau는 데이터를 시각화하고 대시보드를 생성하여 데이터를 분석하고 공유할 수 있는 비즈니스 인텔리전스 도구입니다.",
    "TensorFlow": "TensorFlow는 Google에서 개발한 오픈소스 머신 러닝 프레임워크로, 딥러닝 모델 학습과 배포를 지원합니다.",
    "Terraform": "Terraform은 인프라를 코드로 관리할 수 있도록 지원하는 오픈소스 도구로, 클라우드 리소스를 자동화합니다.",
    "Tomcat": "Apache Tomcat은 Java 서블릿과 JSP(JavaServer Pages)를 실행하기 위한 오픈소스 웹 서버 및 서블릿 컨테이너입니다.",
    "Travis CI": "Travis CI는 GitHub 프로젝트에 통합되어 소프트웨어 빌드와 테스트를 자동화하는 CI/CD 플랫폼입니다.",
    "Trino": "Trino(이전 Presto)는 대규모 분산 SQL 쿼리를 처리하기 위한 고성능 SQL 쿼리 엔진입니다.",
    "TypeScript": "TypeScript는 JavaScript에 정적 타입 기능을 추가한 프로그래밍 언어로, 대규모 애플리케이션 개발에 적합합니다.",
    "Vagrant": "Vagrant는 가상 머신 환경 설정 및 관리를 자동화하여 개발 환경 구축을 간소화하는 도구입니다.",
    "Vim": "Vim은 강력한 텍스트 편집기로, 효율적인 키보드 중심 작업과 커스터마이징이 가능합니다.",
    "VSCode": "Visual Studio Code(VSCode)는 Microsoft에서 제공하는 경량 코드 편집기로, 확장성과 디버깅 기능이 뛰어납니다.",
    "Vue.js": "Vue.js는 사용자 인터페이스와 싱글 페이지 애플리케이션(SPA)을 구축하기 위한 JavaScript 프레임워크입니다.",
    "WebSocket": "WebSocket은 클라이언트와 서버 간의 양방향 통신을 지원하는 프로토콜로, 실시간 데이터 전송에 적합합니다.",
    "WildFly": "WildFly는 Java EE(Java Enterprise Edition) 애플리케이션 실행을 위한 오픈소스 애플리케이션 서버입니다.",
    "Zabbix": "Zabbix는 IT 인프라 모니터링 및 경고 시스템으로, 서버 및 네트워크 장치의 상태를 실시간으로 추적합니다.",
    "Zeppelin": "Apache Zeppelin은 데이터 분석 및 시각화를 위한 웹 기반 노트북으로, 여러 데이터 소스를 통합하여 작업할 수 있습니다."
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

