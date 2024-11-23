import lancedb
from core.config import CONFIG
from core.db_store.db_schemas import Document


class DBStore:
    def __init__(self):
        self.uri = CONFIG.lancedb_uri
        self.db = lancedb.connect(self.uri)
        self.rag_table = self.db.open_table(CONFIG.rag_table_name)

        # TODO: create schema and make the embedding column a vector type.

    def store_documents(self, documents: list[Document]):
        documents_in_dict = [item.model_dump() for item in documents]
        if CONFIG.rag_table_name not in self.db.table_names():
            self.rag_table = self.db.create_table(
                CONFIG.rag_table_name, data=documents_in_dict
            )
        else:
            self.rag_table.add(documents_in_dict)

    def get_documents(self, query: str):
        rag_table = self.db.open_table(CONFIG.rag_table_name)
        results = rag_table.search(query).limit(10).to_list()
        return results

    def vector_search(self, query_embedding: list[float], where_clause: str = ""):
        results = (
            self.rag_table.search(query_embedding)
            .where(where_clause)
            .limit(CONFIG.vector_search_limit)
            .to_list()
        )
        return results


db_utils = DBStore()