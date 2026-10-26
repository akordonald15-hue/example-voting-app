# Build tooling never enters the production filesystem.
FROM python:3.11-alpine@sha256:d9368b3a5ac59afea7b5d4f2e2aea0941dbf9fdee9c369c5bec00b98244bc929 AS build
WORKDIR /build
COPY requirements.txt requirements.lock ./
RUN pip install --ignore-installed --no-cache-dir --only-binary=:all: --require-hashes --prefix=/install -r requirements.lock

FROM build AS dev-dependencies
RUN pip install --no-cache-dir --no-deps --prefix=/devinstall watchdog==6.0.0

FROM python:3.11-alpine@sha256:d9368b3a5ac59afea7b5d4f2e2aea0941dbf9fdee9c369c5bec00b98244bc929 AS base
WORKDIR /usr/local/app
RUN apk add --no-cache musl=1.2.6-r3 musl-utils=1.2.6-r3 zlib=1.3.2-r1 && addgroup -g 1000 app && adduser -D -u 1000 -G app app && chown app:app /usr/local/app &&     rm -rf /usr/local/lib/python3.11/site-packages/* /usr/local/bin/pip /usr/local/bin/pip3 /usr/local/bin/pip3.11
COPY --from=build /install/ /usr/local/
ENV PYTHONDONTWRITEBYTECODE=1

FROM base AS dev
RUN apk add --no-cache curl brotli-libs=1.2.1-r0
COPY --from=dev-dependencies /devinstall/ /usr/local/
ENV FLASK_ENV=development
USER app
CMD ["python", "app.py"]

FROM base AS final
COPY --chown=app:app app.py ./
COPY --chown=app:app templates/ ./templates/
COPY --chown=app:app static/ ./static/
EXPOSE 80
USER app
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:80", "--log-file", "-", "--access-logfile", "-", "--workers", "4", "--keep-alive", "0"]
