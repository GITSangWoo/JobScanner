FROM eclipse-temurin:17-jdk-alpine AS build


ENV JWT_SECRET_KEY=TWVycnlDaHJpa21hdHN0ZWFtMkpvYnNjYW5uZXJQcm9qZWN0QWxtb3N0RG9uZSE=
WORKDIR /land 
COPY . .
RUN ./gradlew clean bootJar

FROM eclipse-temurin:17-jre-alpine AS run
ENV JWT_SECRET_KEY=TWVycnlDaHJpa21hdHN0ZWFtMkpvYnNjYW5uZXJQcm9qZWN0QWxtb3N0RG9uZSE=
COPY --from=build /land/build/libs/*.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
