FROM python:slim

WORKDIR /app
COPY percentage_service.py .

RUN pip install --no-cache-dir flask pika psycopg2-binary python-dateutil python-dotenv

CMD ["python", "percentage_service.py"]