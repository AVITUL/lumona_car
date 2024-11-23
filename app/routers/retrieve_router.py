from fastapi import APIRouter

from app.core.retrieving.retriever import retriever

router = APIRouter()

import logging

logger = logging.getLogger(__name__)


@router.post("/get-answer")
async def get_answer(query: str, context: str):
    logger.info(f"Getting answer for query: {query}")
    answer = retriever.get_answer(query, context)
    return {"answer": answer}
