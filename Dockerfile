FROM gliderlabs/alpine:latest

LABEL maintainer="elastest-users@googlegroups.com"
LABEL description="Builds the service manager docker image."
ARG GIT_COMMIT=unspecified
LABEL git_commit=$GIT_COMMIT
ARG COMMIT_DATE=unspecified
LABEL commit_date=$COMMIT_DATE
ARG VERSION=unspecified
LABEL version=$VERSION

WORKDIR /app
COPY ./src /app

RUN apk --update add --virtual build-deps python3-dev build-base linux-headers
RUN apk --update add python3 py3-pip openssl ca-certificates git \
    && pip3 install --upgrade setuptools \
    && pip3 install -r /app/requirements.txt && rm /app/requirements.txt \
    && apk del build-deps

ENV ESM_PORT 8080
ENV ESM_CHECK_PORT 5000

EXPOSE 8080 5000

CMD ["/usr/bin/python3", "/app/runesm.py"]
