import mysql.connector
from mysql.connector import Error

# RDS MySQL 연결 정보
host = 't2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com'
port = 3306
user = 'admin'
password = 'dltkddn1'
database = 'service'

# 기술 스택 리스트
tech_stack_list = [
    "Jupyter", "Spyder", "PyCharm", "VSCode", "Sublime Text", "Vim", "Emacs", "CI/CD", "Machine Learning", "Deep Learning",
    "Natural Language Processing", "Hadoop", "Spark", "Kafka", "HBase", "Cassandra", "PostgreSQL", "MySQL", "SQLite",
    "MongoDB", "Redis", "Elasticsearch", "Solr", "Apache Storm", "Flume", "Airflow", "Celery", "Apache Camel", "Kotlin", "Java",
    "JavaScript", "TypeScript", "Swift", "Ruby", "Go", "Rust", "PHP", "SQLAlchemy", "JDBC", "Selenium", "Cypress", "Appium",
    "Terraform", "Ansible", "Docker", "Kubernetes", "OpenShift", "Vagrant", "Git", "GitHub", "GitLab", "Bitbucket", "Jenkins",
    "Travis CI", "CircleCI", "Puppet", "Chef", "Nagios", "Prometheus", "Grafana", "Zabbix", "Logstash", "Fluentd", "Loggly",
    "Datadog", "New Relic", "Sentry", "AppDynamics", "GraphQL", "REST API", "gRPC", "WebSocket", "Socket.io", "Nginx",
    "Apache HTTP Server", "Lighttpd", "Tomcat", "Jetty", "WildFly", "Spring Boot", "Spring MVC", "Spring Security", "Spring Cloud",
    "Spring Data", "Spring Batch", "Spring Integration", "Node.js", "Express", "Vue.js", "React", "Angular", "Svelte", "Next.js",
    "Nuxt.js", "Ember.js", "Django", "Flask", "Ruby on Rails", "Laravel", "Spring Framework", "ASP.NET", "Symfony", "Meteor",
    "Hapi", "Golang", "C++", "C#", "C", "Python", "Perl", "CoffeeScript", "Shell", "SQL", "NoSQL", "MariaDB", "Agit", "Tableau",
    "PyTorch", "TensorFlow", "AWS Athena", "LLM", "CSS", "Amazon S3", "AWS Redshift", "Firebase", "Snowflake", "Amazon CloudWatch", "Impala"
]

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

        # 데이터 삽입 쿼리 준비
        insert_query = """
        INSERT INTO tech_stack (tech_name, tech_description)
        VALUES (%s, %s)
        """

        # 데이터 삽입
        for tech in tech_stack_list:
            cursor.execute(insert_query, (tech, "-"))

        # 변경 사항 커밋
        connection.commit()
        print(f"{len(tech_stack_list)}개의 기술 스택이 삽입되었습니다.")

except Error as e:
    print(f"에러 발생: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL 연결이 종료되었습니다.")
