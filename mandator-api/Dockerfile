FROM eclipse-temurin:21-jdk-alpine

WORKDIR /app

COPY pom.xml ./
COPY mvnw ./
COPY .mvn .mvn

# Lade dependencies (für Caching)
RUN ./mvnw dependency:go-offline

COPY src ./src

RUN ./mvnw package -DskipTests

CMD ["java", "-jar", "target/mandator-api-0.0.1-SNAPSHOT.jar"]
