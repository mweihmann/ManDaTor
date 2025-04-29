FROM python:slim

WORKDIR /app
COPY user.py /app/user.py

RUN pip install flask pika

CMD ["python", "user.py"]