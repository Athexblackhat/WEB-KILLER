# much smaller image than debian based python images
FROM python:3.12-slim

LABEL maintainer="Athexblackhat" \
      description="A tool to automate the process of finding and exploiting vulnerabilities in web applications." \
      version="2.1" \
      repository="

WORKDIR /app

RUN apt-get update && apt-get install -y git && apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "run.py"]
