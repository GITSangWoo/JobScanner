import mysql.connector

# MySQL 연결
conn = mysql.connector.connect(
    host="t2rds.cfa60ymesotv.ap-northeast-2.rds.amazonaws.com",
    user="admin",
    password="dltkddn1",
    database="service"
)
cursor = conn.cursor()

# tech_name과 docs_link를 매칭한 딕셔너리
tech_docs = {
    "Airflow": "https://airflow.apache.org/docs/",
    "Amazon CloudWatch": "https://docs.aws.amazon.com/cloudwatch/",
    "Amazon DynamoDB": "https://docs.aws.amazon.com/dynamodb/",
    "Amazon EC2": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html",
    "Amazon EKS": "https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html",
    "Amazon Lambda": "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
    "Amazon Neptune": "https://docs.aws.amazon.com/neptune/latest/userguide/intro.html",
    "Amazon RDS": "https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html",
    "Amazon S3": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html",
    "Amazon SNS": "https://docs.aws.amazon.com/sns/latest/dg/welcome.html",
    "Amazon SQS": "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html",
    "Amazon VPC": "https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html",
    "Angular": "https://angular.io/docs",
    "Ansible": "https://docs.ansible.com/",
    "Apache Camel": "https://camel.apache.org/manual/",
    "Apache Cassandra": "https://cassandra.apache.org/doc/latest/",
    "Apache HTTP Server": "https://httpd.apache.org/docs/",
    "Apache Storm": "https://storm.apache.org/releases/current/index.html",
    "AppDynamics": "https://docs.appdynamics.com/",
    "Appium": "http://appium.io/docs/en/about-appium/intro/",
    "ArangoDB": "https://www.arangodb.com/docs/stable/",
    "ASP.NET": "https://learn.microsoft.com/en-us/aspnet/core/?view=aspnetcore-7.0",
    "AWS Athena": "https://docs.aws.amazon.com/athena/latest/ug/what-is.html",
    "AWS Redshift": "https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html",
    "Berkeley DB": "http://sleepycat.github.io/db.html",
    "Bitbucket": "https://bitbucket.org/product/features",
    "C": "https://en.cppreference.com/w/c/language",
    "C#": "https://learn.microsoft.com/en-us/dotnet/csharp/",
    "C++": "https://cplusplus.com/doc/tutorial/",
    "Cassandra": "https://cassandra.apache.org/doc/latest/",
    "Celery": "https://docs.celeryproject.org/en/stable/",
    "Chef": "https://docs.chef.io/",
    "CircleCI": "https://circleci.com/docs/",
    "CoffeeScript": "http://coffeescript.org/",
    "CSS": "https://developer.mozilla.org/en-US/docs/Web/CSS",
    "Cypress": "https://docs.cypress.io/",
    "Datadog": "https://docs.datadoghq.com/",
    "Deep Learning": "https://www.tensorflow.org/learn",
    "Django": "https://docs.djangoproject.com/en/stable/",
    "Docker": "https://docs.docker.com/",
    "Elasticsearch": "https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html",
    "Emacs": "https://www.gnu.org/software/emacs/manual/",
    "Ember.js": "https://emberjs.com/learn/",
    "Express": "https://expressjs.com/",
    "FastAPI": "https://fastapi.tiangolo.com/",
    "Firebase": "https://firebase.google.com/docs",
    "Flask": "https://flask.palletsprojects.com/en/stable/",
    "Fluentd": "https://docs.fluentd.org/",
    "Flume": "https://flume.apache.org/FlumeUserGuide.html",
    "Git": "https://git-scm.com/doc",
    "GitHub": "https://docs.github.com/en",
    "GitHub Actions": "https://docs.github.com/en/actions",
    "GitLab": "https://docs.gitlab.com",
    "GO": "https://go.dev/doc/",
    "Grafana": "https://grafana.com/docs/",
    "GraphQL": "https://graphql.org/learn/",
    "gRPC": "https://grpc.io/docs/",
    "Hadoop": "https://hadoop.apache.org/docs/",
    "Hapi": "https://hapi.dev/api/",
    "HBase": "https://hbase.apache.org/book.html",
    "Helm": "https://helm.sh/docs/",
    "Hypertable": "http://hypertable.com/documentation/",
    "Impala": "https://impala.apache.org/docs/",
    "Java": "https://docs.oracle.com/en/java/",
    "JavaScript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "JDBC": "https://docs.oracle.com/javase/8/docs/technotes/guides/jdbc/",
    "Jenkins": "https://www.jenkins.io/doc/",
    "Jetty": "https://www.eclipse.org/jetty/documentation/",
    "Jupyter": "https://jupyter.org/documentation",
    "Kafka": "https://kafka.apache.org/documentation/",
    "Kotlin": "https://kotlinlang.org/docs/",
    "Kubernetes": "https://kubernetes.io/docs/",
    "Laravel": "https://laravel.com/docs",
    "Lighttpd": "http://www.lighttpd.net/documentation/",
    "LLM": "https://en.wikipedia.org/wiki/Large_language_model",
    "Loggly": "https://documentation.solarwinds.com/en/success_center/loggly/content/getting-started.htm",
    "Logstash": "https://www.elastic.co/guide/en/logstash/current/index.html",
    "Machine Learning": "https://scikit-learn.org/stable/user_guide.html",
    "MariaDB": "https://mariadb.com/kb/en/documentation/",
    "Meteor": "https://docs.meteor.com/",
    "MongoDB": "https://www.mongodb.com/docs/",
    "MySQL": "https://dev.mysql.com/doc/",
    "Nagios": "https://nagios.fm4dd.com/docs/en/",
    "Natural Language Processing": "",
    "Neo4j": "https://neo4j.com/docs/",
    "New Relic": "https://docs.newrelic.com",
    "Next.js": "https://nextjs.org/docs",
    "Nginx": "https://nginx.org/en/docs/",
    "Node.js": "https://nodejs.org/en/docs/",
    "NoSQL": "https://www.mongodb.com/nosql-explained",
    "Nuxt.js": "https://nuxt.com/docs",
    "OpenShift": "https://docs.openshift.com",
    "Oracle": "https://docs.oracle.com/en/database/oracle/oracle-database/",
    "OrientDB": "https://orientdb.org/docs/",
    "Perl": "https://perldoc.perl.org/",
    "PHP": "https://www.php.net/docs.php",
    "PostgreSQL": "https://www.postgresql.org/docs/",
    "Prometheus": "https://prometheus.io/docs/",
    "Puppet": "https://puppet.com/docs/puppet/latest/puppet_index.html",
    "PyCharm": "https://www.jetbrains.com/pycharm/documentation/",
    "Python": "https://docs.python.org/3/",
    "PyTorch": "https://pytorch.org/docs/1.12/",
    "React": "https://react.dev",
    "Redash": "https://redash.io/help/",
    "Redis": "https://redis.io/docs/latest/",
    "REST API": "https://restfulapi.net/",
    "Riak": "http://docs.basho.com/riak/latest/",
    "Ruby": "https://www.ruby-lang.org/en/documentation/",
    "Ruby on Rails": "https://guides.rubyonrails.org",
    "Rust": "https://doc.rust-lang.org/",
    "ScyllaDB": "https://docs.scylladb.com",
    "Selenium": "https://www.selenium.dev/documentation/",
    "Sentry": "https://docs.sentry.io",
    "Shell": "https://www.gnu.org/software/bash/manual/bashref.html",
    "Snowflake": "https://docs.snowflake.com",
    "Socket.io": "https://socket.io/docs/v4/",
    "Solr": "https://solr.apache.org/guide/",
    "Spark": "https://spark.apache.org/docs/latest/",
    "Spring Batch": "https://docs.spring.io/spring-batch/reference/",
    "Spring Boot": "https://docs.spring.io/spring-boot/",
    "Spring Cloud": "https://spring.io/projects/spring-cloud",
    "Spring Data": "https://docs.spring.io/spring-data/",
    "Spring Framework": "https://docs.spring.io/spring-framework/reference/",
    "Spring Integration": "https://docs.spring.io/spring-integration/api/",
    "Spring MVC": "https://docs.spring.io/spring-framework/reference/web/webmvc.html",
    "Spring Security": "https://docs.spring.io/spring-security/reference/",
    "Spyder": "https://docs.spyder-ide.org/",
    "SQL": "https://www.postgresql.org/docs/current/sql.html",
    "SQLAlchemy": "https://docs.sqlalchemy.org/en/20/",
    "SQLite": "https://www.sqlitetutorial.net/",
    "Sublime Text": "https://docs.sublimetext.io/guide/",
    "Svelte": "https://svelte.dev/docs",
    "Swift": "https://swift.org/documentation/",
    "Symfony": "https://symfony.com/doc/current/index.html",
    "Tableau": "https://help.tableau.com/current/guides/index.htm",
    "TensorFlow": "https://www.tensorflow.org/learn",
    "Terraform": "https://developer.hashicorp.com/terraform/docs",
    "Tomcat": "https://tomcat.apache.org/tomcat-9.0-doc/index.html",
    "Travis CI": "https://docs.travis-ci.com/",
    "Trino": "https://trino.io/docs/current/index.html",
    "TypeScript": "https://www.typescriptlang.org/docs/",
    "Vagrant": "https://developer.hashicorp.com/vagrant/docs",
    "Vim": "https://vimhelp.org/",
    "VSCode": "https://code.visualstudio.com/docs",
    "Vue.js": "https://vuejs.org/guide/introduction.html",
    "WebSocket": "",
    "WildFly": "https://docs.wildfly.org",
    "Zabbix": "https://www.zabbix.com/documentation/current/manual",
    "Zeppelin": "https://zeppelin.apache.org/docs/latest/"
}

# SQL 업데이트 쿼리
update_query = """
UPDATE tech_stack
SET docs_link = %s
WHERE tech_name = %s
"""

# 성공적으로 업데이트된 항목 수를 저장할 변수
success_count = 0

# 각 기술에 대해 docs_link 값을 업데이트
for tech, docs_link in tech_docs.items():
    try:
        cursor.execute(update_query, (docs_link, tech))
        success_count += 1  # 성공적으로 업데이트된 경우 카운트 증가
    except mysql.connector.Error as err:
        print(f"Error updating {tech}: {err}")

# 변경 사항 커밋 및 연결 종료
conn.commit()
cursor.close()
conn.close()

# 총 업데이트된 항목 수 출력
print(f"총 {success_count}개의 docs_link가 삽입되었습니다.")
