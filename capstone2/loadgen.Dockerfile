# Context: capstone2. Keep upstream traffic logic, replace EOL Python/unlocked install.
# Resolve/review a hash-locked Locust graph into loadgen-requirements.lock first.
FROM python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f AS dependencies
WORKDIR /build
COPY loadgen-requirements.lock ./
RUN pip install --no-cache-dir --require-hashes --prefix=/install -r loadgen-requirements.lock
FROM python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f
WORKDIR /load
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid 1000 --no-create-home app
COPY --from=dependencies /install/ /usr/local/
COPY --chown=app:app upstream-source/load-gen/entrypoint.sh local-services/loadgen/robot-shop.py ./
RUN chmod 0555 /load/entrypoint.sh
ENV NUM_CLIENTS=1 RUN_TIME=5m ERROR=0 SILENT=0 PYTHONDONTWRITEBYTECODE=1
USER app
CMD ["/load/entrypoint.sh"]
