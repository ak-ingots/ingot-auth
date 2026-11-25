# PYTHON: the newest of PYTHONS, as a new application starts on it.
ARG PYTHON
FROM python:${PYTHON}-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv
COPY dist/ /dist/
RUN uv pip install --system --no-cache -r /dist/web-requirements.txt \
    "$(ls /dist/*.whl)[web]"
WORKDIR /srv
# the root of the example is that of the application, its modules on sys.path,
# uvicorn taking its working directory as the directory of the application
COPY examples/web/ ./
ENTRYPOINT ["uvicorn"]
CMD ["asgi:app", "--host", "0.0.0.0", "--port", "8000"]
