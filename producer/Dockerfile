FROM python:slim

WORKDIR /app
COPY producer.py /app/producer.py

RUN pip install flask pika

CMD ["python", "producer.py"]