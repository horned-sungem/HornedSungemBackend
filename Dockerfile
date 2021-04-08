FROM python:3
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

RUN pip install -r requirements.txt