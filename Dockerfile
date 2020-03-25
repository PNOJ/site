FROM python:3-alpine

LABEL maintainer="Kyunghan (Paul) Lee <contact@paullee.dev>"

RUN apk update

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    python3-dev \
    musl-dev \
    postgresql-dev \
    && pip install --no-cache-dir psycopg2 \
    && apk del --no-cache .build-deps

RUN apk add --no-cache libpq

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "pnoj.wsgi", "-b", "0.0.0.0:8000"]
