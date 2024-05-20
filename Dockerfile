FROM python:3.11
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONPATH /opt/src
ENV DJANGO_SETTINGS_MODULE=propylon_document_manager.site.settings.local

RUN apt-get update && apt-get install -y build-essential python3-dev libldap2-dev libsasl2-dev
RUN pip3 install pip poetry

RUN mkdir /opt/src

WORKDIR /opt/
COPY ./pyproject.toml /opt/pyproject.toml
COPY ./poetry.lock /opt/poetry.lock
COPY ./tests /opt/tests
COPY ./src /opt/src/

COPY ./manage.py /opt/manage.py

RUN poetry install --no-interaction
