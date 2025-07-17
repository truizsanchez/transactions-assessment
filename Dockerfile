FROM python:3.12 as base

ENV APP_DIR=/srv \
    APP_USER="developers" \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONPATH=/srv/src \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR ${APP_DIR}

RUN pip install poetry

ARG UID=1000
ARG GID=1000
RUN (groupadd -g ${GID} -r ${APP_USER} \
    || groupmod --new-name ${APP_USER} `getent group ${GID} | cut --delimiter=: -f1`) \
    && useradd -u ${UID} -r -m \
    -g ${APP_USER} ${APP_USER} \
    -s /usr/sbin/nologin \
    --home-dir ${APP_DIR}

COPY pyproject.toml ${APP_DIR}/pyproject.toml
COPY poetry.lock ${APP_DIR}/poetry.lock
COPY README.md ${APP_DIR}/README.md

ADD . ${APP_DIR}/

RUN poetry install

USER $APP_USER

EXPOSE 8000
