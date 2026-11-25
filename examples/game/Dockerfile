# PYTHON: the newest of PYTHONS, as a new application starts on it.
ARG PYTHON
FROM python:${PYTHON}-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
COPY dist/ /dist/
RUN uv pip install --system --no-cache -r /dist/game-requirements.txt \
    "$(ls /dist/*.whl)[game]"
WORKDIR /srv
# the root of the example is that of the application, its modules on sys.path
COPY examples/game/ ./
ENTRYPOINT ["python", "/srv"]
CMD ["components", "run-forever", "--component", "grpc.servers.default"]
