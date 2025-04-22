FROM python:slim

WORKDIR /app
COPY user.py /app/user.py

RUN pip install flask pika

EXPOSE 5002
CMD ["python", "user.py"]