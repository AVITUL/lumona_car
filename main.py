import logging

from fastapi import FastAPI

from app.routers import index_router, retrieve_router

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting the application...")

app.include_router(index_router.router, prefix="/indexing")
app.include_router(retrieve_router.router, prefix="/search")
