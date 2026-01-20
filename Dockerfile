FROM amazoncorretto:23-alpine-jdk AS build
WORKDIR /workspace/app

# Copy gradle wrapper and build files
COPY gradle gradle
COPY build.gradle settings.gradle gradlew ./
COPY src src

# Build
RUN ./gradlew clean build -x test

# Runtime Stage
FROM amazoncorretto:23-alpine
VOLUME /tmp
ARG DEPENDENCY=/workspace/app/build/libs
COPY --from=build ${DEPENDENCY}/*.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]