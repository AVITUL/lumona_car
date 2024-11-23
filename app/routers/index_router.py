from fastapi import APIRouter

router = APIRouter()

@router.post("/index-document")
async def index_document(document: str):
    pass

