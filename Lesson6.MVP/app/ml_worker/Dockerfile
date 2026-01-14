FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

CMD ["python", "ml_worker/main.py"]

