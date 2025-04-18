FROM python:3.11-slim
RUN apt-get update && apt-get install -y iputils-ping traceroute net-tools curl wget dnsutils iproute2 file vim && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 8000
CMD ["python", "app.py"]