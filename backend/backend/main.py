"""API wrapper around backend logic."""

from fastapi import FastAPI

from backend.middleware.error_handler import register_global_error_handler
from backend.routes import auth, core

app = FastAPI(debug=True)
register_global_error_handler(app)
app.include_router(auth.router)
app.include_router(core.router)
