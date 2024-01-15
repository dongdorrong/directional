#!/bin/bash
# Terminate prior application
pid=$(sudo netstat -nlp | grep ':8080' | grep 'java' | awk '{print $7}' | cut -d'/' -f1)

# Check if the PID was found
if [ -z "$pid" ]; then
    echo "No Java process found on port 8080."
else
    echo "Killing Java process with PID $pid on port 8080."
    # Kill the process
    sudo kill -9 $pid
fi

GRADLE_CMD="./gradlew"
PROFILE="django"

SPRING_BOOT_JAR="application-major.minor.patch.jar"

cd /home/ubuntu/directory

echo "Building Spring Boot Application..."
$GRADLE_CMD clean build -x test -Pprofile='$PROFILE'

cd /home/ubuntu/directiory

if [ $? -eq 0 ]; then
 echo "Starting Spring Boot Application with '$PROFILE' profile..."
 sudo nohup java -jar -Dspring.profiles.active=django  build/libs/$SPRING_BOOT_JAR -Dspring.config.location=build/resources/main &
else
 echo "Build failed. Check the Gradle build output for errors."
fi
