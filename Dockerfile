FROM alpine:3.9

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk update && \
	apk add ca-certificates && \
	update-ca-certificates && \
	apk add wget && \
	pip3 install --upgrade pip && \
	pip3 install --upgrade setuptools && \
	apk add build-base libffi-dev coreutils openssl-dev python3-dev nodejs bind-tools curl jq && \
	pip3 install --no-cache-dir python-dateutil && \
	pip3 install --no-cache-dir edgegrid-python

# Embeds mPulse Annotator python files to docker image
RUN mkdir /root/ak-mpulse-annotator
ADD *.py /root/ak-mpulse-annotator/

# Customizations
ENV ENV="/etc/profile"
RUN echo "alias ll='ls -la'" >> "$ENV"

WORKDIR /root/ak-mpulse-annotator