ARG APP_BUILD_DEPS="build-essential"
ARG APP_RUN_DEPS=""
ARG DEV_BUILD_DEPS=""
ARG DEV_RUN_DEPS="make git vim zip unzip"

FROM python:3.9-slim AS base

ARG APP_BUILD_DEPS
ARG APP_RUN_DEPS

COPY requirements.txt /requirements.txt

RUN apt-get update && \ 
    apt-get install ${APP_BUILD_DEPS} -y && \
    apt-get install ${APP_RUN_DEPS} -y && \
    python -m pip install --upgrade pip && \
    pip install -r /requirements.txt && \
    rm /requirements.txt && \
    apt-get remove ${APP_BUILD_DEPS} -y

FROM base as app

# ARG APP_BUILD_DEPS
# ARG APP_RUN_DEPS

# RUN apt-get install ${APP_BUILD_DEPS} -y && \
#     apt-get install ${APP_RUN_DEPS} -y && \
#     apt-get remove ${APP_BUILD_DEPS} -y

FROM base as dev

ARG DEV_BUILD_DEPS
ARG DEV_RUN_DEPS

COPY requirements.dev.txt /requirements.dev.txt

RUN apt-get install ${DEV_BUILD_DEPS} -y && \
    apt-get install ${DEV_RUN_DEPS} -y && \
    pip install -r /requirements.dev.txt && \
    rm /requirements.dev.txt && \
    apt-get remove ${DEV_BUILD_DEPS} -y

WORKDIR /zda/dev