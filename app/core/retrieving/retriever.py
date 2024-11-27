import logging
from typing import Any, Tuple

import pandas as pd

from app.core.config import CONFIG

# from app.core.db_store.db_mongo import db_mongo
from app.core.db_store.db_ops import db_utils
from app.core.ml.embedding_handler import embedding_handler
from app.core.ml.llm_handler import llm_caller
from app.core.ml.prompts import (
    answer_question_prompt,
    build_query_prompt,
    is_answerable_prompt,
)
from app.core.retrieving.retrieving_schemas import (
    AnswerLLMResponseSchema,
    IsAnswerableSchema,
    QuerySchema,
)

logger = logging.getLogger(__name__)


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

    def _answer_to_md(self, llm_response: AnswerLLMResponseSchema) -> str:
        answer_md = ""
        refs_count = 1
        final_references_list = []
        ref_map = {}
        for answer_sentence in llm_response.sentences:
            answer_md += f"{answer_sentence.sentence_text}\n"
            if answer_sentence.sentence_document_ref:
                if answer_sentence.sentence_document_ref in ref_map:
                    ref_num = ref_map[answer_sentence.sentence_document_ref]
                else:
                    ref_num = refs_count
                    ref_map[answer_sentence.sentence_document_ref] = refs_count
                    refs_count += 1
                answer_md += f"[{ref_num}]({answer_sentence.sentence_document_ref})\n"
        final_references_list.append(answer_sentence.sentence_document_ref)
        answer_md += "\n\nReferences:\n"
        for ref in final_references_list:
            try:
                doc = db_utils.get_document_by_ref(ref)
                if doc:
                    answer_md += (
                        f"<details><raw_data>{ref}</raw_data>\n\n{doc}\n\n</details>\n"
                    )
            except Exception as e:
                logger.exception(f"Error fetching document {ref}: {e}")
        return answer_md

    def _answer_question(self, question: str, similar_docs_df: Any) -> str:
        llm_response: AnswerLLMResponseSchema = llm_caller.generate_structured_response(
            output_schema=AnswerLLMResponseSchema,
            system_prompt=answer_question_prompt.PROMPT,
            question=question,
            input_data=similar_docs_df,
        )  # type: ignore
        answer = self._answer_to_md(llm_response)
        return answer

    def _is_question_answerable(self, question: str, context: str) -> Tuple[bool, str]:
        try:
            llm_response: IsAnswerableSchema = llm_caller.generate_structured_response(
                output_schema=IsAnswerableSchema,
                system_prompt=is_answerable_prompt.PROMPT,
                question=question,
            )  # type: ignore
            logger.info(
                f"Is question answerable: {llm_response.is_answerable}, reasoning: {llm_response.reasoning}"
            )
            return llm_response.is_answerable, llm_response.reasoning
        except Exception as e:
            logger.exception(f"Error in is_question_answerable: {e}")
            return False, "I am sorry, I am not able to answer that question."

    def get_answer(self, question: str, context: str) -> str:
        try:
            logger.info(f"Checking if question is answerable")
            is_question_answerable, reason = self._is_question_answerable(
                question, context
            )
            if not is_question_answerable:
                return f"I am sorry, I am not able to answer that question. {reason}"

            logger.info(f"Embedding question")
            try:
                question_embedding = embedding_handler.embed_text(question)
            except Exception as e:
                logger.exception(f"Error in embedding question: {e}")
                return "Unknown error."

            logger.info(f"Building query")
            where_clause = self._build_query(question)  # add after testing.
            if question_embedding is None:
                raise ValueError("Question embedding is None")

            input_documents = ""
            logger.info(f"Vector search")
            if CONFIG.database_type == "mongo":
                # similar_docs = db_mongo.get_documents_with_vector_search(
                #     question_embedding
                # )
                # input_documents = similar_docs
                pass
            else:
                similar_docs = db_utils.vector_search(question_embedding)
                similar_docs_df = pd.DataFrame(similar_docs)
                input_documents = similar_docs_df[["text", "type", "id"]].to_json(
                    orient="records"
                )
            logger.info(f"Got similar docs {len(similar_docs)}")
            answer = self._answer_question(question, input_documents)
            return answer
        except Exception as e:
            logger.error(f"Error in get_answer: {e}")
            return "Unknown error."


retriever = Retriever()
