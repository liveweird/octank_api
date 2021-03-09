FROM python:3.8.8-slim-buster
WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# RUN alembic upgrade head
EXPOSE 80
ENV FLASK_APP=octank_api
ENV FLASK_RUN_PORT=80
CMD [ "flask", "run" ]