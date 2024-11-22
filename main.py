import logging

from fastapi import FastAPI

from app.routers import indexer, retriever

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting the application...")

app.include_router(indexer.router, prefix="/indexing")
app.include_router(retriever.router, prefix="/search")
