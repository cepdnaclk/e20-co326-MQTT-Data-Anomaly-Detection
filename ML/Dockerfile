FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --default-timeout=3000 --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "brain.py"]