from pydantic import BaseModel


class AnswerSentenceSchema(BaseModel):
    sentence_text: str
    sentence_document_ref: str
    sentence_parent_href: str | None = None
    # given that the questions might be from a single car this value will remain constant.


class RetrieverResponseSchema(BaseModel):
    question_text: str
    question_id: str
    retrieved_document_ids: list[str]
    answer_text: list[AnswerSentenceSchema]


class AnswerLLMResponseSchema(BaseModel):
    sentences: list[AnswerSentenceSchema]


class QuerySchema(BaseModel):
    keywords: list[str]
    car_model: str | None = None
    tags: list[str]
    type: str


class IsAnswerableSchema(BaseModel):
    is_answerable: bool
    reasoning: str
