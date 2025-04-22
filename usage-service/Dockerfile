FROM python:slim

WORKDIR /app
COPY usage_service.py .

RUN pip install --no-cache-dir flask pika psycopg2-binary python-dateutil python-dotenv

CMD ["python", "usage_service.py"]