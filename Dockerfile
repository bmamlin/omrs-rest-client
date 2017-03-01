FROM python:3-slim

RUN apt-get update && \
	pip install requests pyyaml python-dateutil

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/python"]