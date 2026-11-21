# The game, as an application is installed: the wheel of ingot-auth that
# `make all` builds, with its extra `game` at the versions of uv.lock, which
# `make example-test` exports next to it; then the code of the application.
# Built from the root of the repository, on the newest Python of PYTHONS in
# the Makefile, as a new application starts on it.
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
