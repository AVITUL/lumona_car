from fastapi import APIRouter

from app.core.retrieving.retriever import retriever

router = APIRouter()

import logging

logger = logging.getLogger(__name__)

from pydantic import BaseModel


class GetAnswerRequest(BaseModel):
    query: str
    context: str


@router.post("/get-answer")
async def get_answer(request: GetAnswerRequest):
    logger.info(f"Getting answer for query: {request.query}")
    answer = retriever.get_answer(request.query, request.context)
    return {"answer": answer}
