FROM python:3.8.8-slim-buster
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# RUN alembic upgrade head
EXPOSE 80
ENV FLASK_APP=octank_api
ENV FLASK_RUN_PORT=80
ENV FLASK_RUN_HOST=0.0.0.0
ENV LISTEN_ADDRESS=127.0.0.1:80
ENV OTEL_EXPORTER_OTLP_ENDPOINT=127.0.0.1:4317
CMD [ "flask", "run" ]