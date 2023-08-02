FROM python:3.11.3-slim-buster
WORKDIR /app/
COPY requirements.txt /app/

RUN apt-get update && apt-get install build-essential git -y
RUN pip install -U pip && pip install -r requirements.txt
COPY *.py /app/
COPY *.sh /app/
RUN mkdir /app/app/
RUN mkdir /app/data/
COPY app/*.py /app/app/
ENTRYPOINT /app/entrypoint.sh
