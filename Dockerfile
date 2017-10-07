FROM python:3.6
RUN apt-get update -y
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /opt/code
WORKDIR /opt/code
