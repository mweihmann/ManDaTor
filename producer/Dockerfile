FROM python:slim

WORKDIR /app
COPY producer.py /app/producer.py

RUN pip install flask pika requests pytz

CMD ["python", "producer.py"]