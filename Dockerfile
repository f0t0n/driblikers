# base image
FROM python:3.5-alpine

# setup working directory
ENV APP_DIR '/usr/local/app'
ENV PATH "$PATH:$APP_DIR"
WORKDIR "/usr/local/app"

# setup group/user
RUN set -ex \
    && addgroup -g '120' -S 'worker' \
    && adduser -u '120' -G 'worker' -S -s '/bin/false' \
        -h '$APP_DIR' 'worker'

# install required packages
RUN set -ex \
    && apk add --no-cache \
        g++ \
        gcc \
        gettext \
        git \
        libffi-dev \
        make \
        openssh-client \
        postgresql-dev \
        su-exec

# install gunicorn
RUN set -ex \
    && pip install --no-cache-dir \
        gunicorn=='19.6.0'

# setup custom python packages base directory
# it is required to use pip with --user flag
ENV PYTHONUSERBASE '/pip-cache'
ENV PATH "$PYTHONUSERBASE/bin:$PATH"

# install app
COPY requirements.txt .
RUN set -ex \
    && pip install --user --requirement ./requirements.txt
COPY . .

# default command
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["python", "driblikers/instance.py", "justinpervorse"]

