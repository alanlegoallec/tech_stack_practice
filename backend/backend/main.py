"""API wrapper around backend logic."""

import logging

from fastapi import FastAPI

from backend.api.routes import auth, core
from backend.core.error_handlers import register_global_error_handlers

# Set up logging
logger = logging.getLogger(__name__)

# Create the FastAPI app
app = FastAPI(debug=True)

# Register global exception handlers
register_global_error_handlers(app)

# Register routes
app.include_router(auth.router)
app.include_router(core.router)
