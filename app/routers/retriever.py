from fastapi import APIRouter

router = APIRouter()

@router.post("/get-answer")
async def get_answer(query: str, context: str):
    pass
