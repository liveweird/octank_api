FROM python:3.8.8-slim-buster
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# RUN alembic upgrade head
# RUN opentelemetry-bootstrap --action=install
EXPOSE 80
ENV FLASK_APP=octank_api
ENV FLASK_RUN_PORT=80
ENV FLASK_RUN_HOST=0.0.0.0
ENV OTEL_RESOURCE_ATTRIBUTES='service.name=octank-api'
# CMD opentelemetry-instrument python3 -m flask run
CMD python3 -m flask run