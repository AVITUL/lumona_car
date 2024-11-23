import pandas as pd
from pydantic.v1 import BaseModel

from app.core.config import CONFIG
from app.core.db_store.db_ops import db_utils
from app.core.ml.embedding_handler import embedding_handler
from app.core.ml.llm_handler import llm_caller
from app.core.ml.prompts import answer_question_prompt, build_query_prompt
from app.core.retrieving.retrieving_schemas import QuerySchema, RetrieverResponseSchema


class Retriever:
    def __init__(self):
        self.retrieval_strategy = CONFIG.retrieval_strategy

    def _build_query(self, question: str) -> str:
        llm_response: QuerySchema = llm_caller.generate_structured_response(
            output_schema=QuerySchema,
            system_prompt=build_query_prompt.PROMPT,
            question=question,
        )  # type: ignore

        where_conditions = []
        if llm_response.type:
            where_conditions.append(f"type = '{llm_response.type}'")
        if llm_response.tags:
            where_conditions.append(f"tag IN {llm_response.tags}")
        if llm_response.car_model:
            where_conditions.append(f"car_model = '{llm_response.car_model}'")

        where_clause = " AND ".join(where_conditions)
        return where_clause

    def _answer_to_md(self, llm_response: RetrieverResponseSchema) -> str:
        answer_md = ""
        refs_count = 1
        final_references_list = []
        for answer_sentence in llm_response.answer_text:
            answer_md += f"{answer_sentence.sentence_text}\n"
            if answer_sentence.sentence_document_ref:
                answer_md += (
                    f"[{refs_count}]({answer_sentence.sentence_document_ref})\n"
                )
                refs_count += 1
        final_references_list.append(answer_sentence.sentence_document_ref)
        answer_md += "\n\nReferences:\n"
        for ref in final_references_list:
            answer_md += f"[{ref}]({ref})\n"  # TODO: add parent document name to the database, retrieve it and show here.
        return answer_md

    def _answer_question(self, question: str, similar_docs_df: pd.DataFrame) -> str:
        llm_response: RetrieverResponseSchema = llm_caller.generate_structured_response(
            output_schema=RetrieverResponseSchema,
            system_prompt=answer_question_prompt.PROMPT,
            question=question,
            similar_docs_df=similar_docs_df,
        )  # type: ignore
        answer = self._answer_to_md(llm_response)
        return answer

    def get_answer(self, question: str, context: str) -> str:
        question_embedding = embedding_handler.embed_text(question)
        where_clause = self._build_query(question)
        if question_embedding is None:
            raise ValueError("Question embedding is None")
        similar_docs = db_utils.vector_search(question_embedding, where_clause)
        similar_docs_df = pd.DataFrame(similar_docs)
        answer = self._answer_question(question, similar_docs_df)
        return answer


retriever = Retriever()
