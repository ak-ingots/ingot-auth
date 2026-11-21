"""The site in the process of a server: ``uvicorn asgi:app``, from its root."""

from ingot_starlette.runner import StarletteRunner

from project import AppProject

app = StarletteRunner(AppProject)
