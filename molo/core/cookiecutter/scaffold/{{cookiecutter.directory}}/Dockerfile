FROM ubuntu:14.04
MAINTAINER {{cookiecutter.full_name}} {{cookiecutter.email}}
RUN apt-get update && apt-get -y --force-yes install libjpeg-dev zlib1g-dev libxslt1-dev libpq-dev nginx redis-server supervisor python-dev python-pip
RUN apt-get -y install libffi-dev gettext

RUN pip install --upgrade pip

ENV PROJECT_ROOT /deploy/
ENV DJANGO_SETTINGS_MODULE {{cookiecutter.app_name}}.settings.docker

WORKDIR /deploy/

COPY {{cookiecutter.app_name}} /deploy/{{cookiecutter.app_name}}
ADD manage.py /deploy/
ADD requirements.txt /deploy/
ADD setup.py /deploy/
ADD README.rst /deploy/
ADD VERSION /deploy/

RUN pip install -e .

RUN mkdir -p /etc/supervisor/conf.d/
RUN mkdir -p /var/log/supervisor
RUN rm /etc/nginx/sites-enabled/default

ADD docker/nginx.conf /etc/nginx/sites-enabled/molo.conf
ADD docker/supervisor.conf /etc/supervisor/conf.d/molo.conf
ADD docker/supervisord.conf /etc/supervisord.conf
ADD docker/docker-start.sh /deploy/
ADD docker/settings.py /deploy/{{cookiecutter.app_name}}/settings/docker.py

RUN chmod a+x /deploy/docker-start.sh

EXPOSE 80

ENTRYPOINT ["/deploy/docker-start.sh"]
