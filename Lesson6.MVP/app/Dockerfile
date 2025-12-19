# FROM python:3.10-slim

# WORKDIR /app

# COPY requirements.txt /app/

# RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# EXPOSE 8080

# CMD ["python", "api.py"]

FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "api.py"]