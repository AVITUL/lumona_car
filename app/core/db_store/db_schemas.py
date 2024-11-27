from typing import Literal

from pydantic import BaseModel


class Document(BaseModel):
    # this is the most granular unit of data for RAG.
    id: str
    text: str
    metadata: dict
    parent_document_id: str | None = None
    type: Literal["TABLE", "CONTENTS", "FIGURE", "PAGE", "PARAGRAPH"] = "PAGE"
    embedding: list[float] | None = None
    keywords: list[str] | None = None
    ref_in_parent: int | None = None
    tag: Literal[
        "RECOMMENDATION", "COMPONENT", "FEATURE", "OPERATIONAL_GUIDE", "OTHER"
    ] = "OTHER"
    previous_document_id: str | None = None
    next_document_id: str | None = (
        None  # we use these if there is information ambiguity in the future.
    )


class ParentDocument(BaseModel):
    # this is the highest level of data for RAG.
    id: str
    title: str
    content: str
    children: list[Document]
    metadata: dict
    type: str


class CarSchema(BaseModel):
    id: str
    name: str


# TODO: think if we are to use a hierarchical clustering how these will change.
