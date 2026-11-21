`examples/game` and `examples/web` are laid out as an application is: at
their root `project.py`, collecting `extensions/`, a module each for what
they extend, the settings, the logging, the auth, the mail and the
transport, run as `python .` and `uvicorn asgi:app` from it.
