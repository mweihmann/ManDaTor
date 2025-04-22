FROM python:slim

WORKDIR /app
COPY producer.py /app/producer.py

RUN pip install flask pika

EXPOSE 5001
CMD ["python", "producer.py"]