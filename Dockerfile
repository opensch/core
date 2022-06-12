FROM python:3.10-buster
LABEL maintainer="openSchool"

COPY . /app
RUN rm -rf /app/docker
RUN rm /app/Dockerfile

RUN apt-get update 
RUN apt-get install -y nginx

COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/nginx.conf.ssl /etc/nginx/nginx.conf.ssl
COPY docker/runner.sh /app/runner.sh
RUN chmod +x /app/runner.sh

WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install flup

CMD ["bash", "/app/runner.sh"]
