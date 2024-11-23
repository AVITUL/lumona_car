from app.core.config import CONFIG
from app.core.db_store.db_ops import db_utils
from app.core.ml.embedding_handler import embedding_handler


class Retriever:
    def __init__(self):
        self.retrieval_strategy = CONFIG.retrieval_strategy

    def get_answer(self, query: str, context: str):
        question_embedding = embedding_handler.embed_text(query)
        if question_embedding is None:
            raise ValueError("Question embedding is None")
        similar_docs_df = db_utils.vector_search(question_embedding)


retriever = Retriever()
