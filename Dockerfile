FROM python:3.8-buster

WORKDIR /app

ADD app app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

VOLUME /app/instances
VOLUME /app/logs

ENV FILENAME="logs/info.log"
ENV DATABASE_URL="instances/prod-sql.db"

CMD ["uvicorn", "app:app", "--host=0.0.0.0", "--port=80", "--workers=10"]
