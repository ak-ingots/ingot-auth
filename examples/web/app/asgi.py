"""The site in the process of a server: ``uvicorn app.asgi:app``."""

from ingot_starlette.runner import StarletteRunner

from .project import AppProject

app = StarletteRunner(AppProject)
