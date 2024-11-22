from pydantic import BaseModel
from typing import Literal

class Document(BaseModel): 
    # this is the most granular unit of data for RAG. 
    text: str
    metadata: dict
    parent_document_id: str | None = None
    type: Literal["TABLE", "CONTENTS", "FIGURE", "PAGE", "PARAGRAPH"]
    embedding: list[float] | None = None
    keywords: list[str] | None = None
    ref_in_parent: int | None = None
    tag: Literal["RECOMMENDATION", "COMPONENT", "FEATURE", "OPERATIONAL_GUIDE", "OTHER"] = "OTHER"

class ParentDocument(BaseModel):
    # this is the highest level of data for RAG. 
    id: str
    title: str
    content: str
    children: list[Document]
    metadata: dict
    type: str 

# TODO: think if we are to use a hierarchical clustering how these will change. 
