from langchain_huggingface import HuggingFaceEmbeddings
from openai import OpenAI

from app.core.config import CONFIG


class EmbeddingHandler:
    def __init__(self, embedding_model: str):
        self.embedding_model = embedding_model
        if embedding_model == "openai":
            self.openai_client = OpenAI(api_key=CONFIG.openai_key)
            self.model = CONFIG.openai_embedding_model
        elif embedding_model == "huggingface":
            self.huggingface_client = HuggingFaceEmbeddings(
                model_name=CONFIG.huggingface_embedding_model
            )
        else:
            raise ValueError(f"Invalid embedding model: {embedding_model}")

    def _embed_text_openai(self, text: str):
        embedding = self.openai_client.embeddings.create(input=text, model=self.model)
        return embedding.data[0].embedding

    def _embed_text_huggingface(self, text: str):
        embedding = self.huggingface_client.embed_query(text)
        return embedding

    def embed_text(self, text: str):
        if self.embedding_model == "openai":
            return self._embed_text_openai(text)
        elif self.embedding_model == "huggingface":
            return self._embed_text_huggingface(text)


embedding_handler = EmbeddingHandler(CONFIG.default_embedding_model)
