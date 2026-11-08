FROM eclipse-temurin:21-jre AS java-runtime

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_HOME=/opt/java/openjdk \
    PATH="/opt/java/openjdk/bin:${PATH}" \
    GAME_LAB_JAVA_EXECUTABLE=/opt/java/openjdk/bin/java \
    GAME_LAB_PARSER_JAR=/opt/gd-edit/gd-edit-standalone.jar \
    GAME_LAB_PARSER_WORKER_SOURCE=/opt/game-lab/parser-worker/src

COPY --from=java-runtime /opt/java/openjdk /opt/java/openjdk

WORKDIR /app

COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --requirement requirements.txt

COPY scripts/package_gd_edit.py /tmp/package_gd_edit.py
RUN python /tmp/package_gd_edit.py --destination /opt/gd-edit \
    && rm /tmp/package_gd_edit.py

COPY apps/api/app ./app
COPY apps/api/data ./data
COPY apps/parser-worker/src /opt/game-lab/parser-worker/src

USER 65532:65532

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
