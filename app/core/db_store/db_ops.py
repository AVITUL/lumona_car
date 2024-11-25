import lancedb
import pyarrow as pa

from app.core.config import CONFIG
from app.core.db_store.db_schemas import Document


class DBStore:
    def __init__(self):
        self.uri = CONFIG.lancedb_uri
        self.db = lancedb.connect(self.uri)
        if CONFIG.rag_table_name in self.db.table_names():
            self.rag_table = self.db.open_table(CONFIG.rag_table_name)
        else:
            embedding_length = CONFIG.embedding_length
            embedding_type = pa.list_(pa.float32(), embedding_length)
            schema = pa.schema(
                [
                    pa.field("id", pa.string()),
                    pa.field("text", pa.string()),
                    pa.field("parent_document_id", pa.string()),
                    pa.field("type", pa.string()),
                    pa.field("embedding", embedding_type),
                    pa.field("keywords", pa.string()),
                    pa.field("ref_in_parent", pa.int64()),
                    pa.field("tag", pa.string()),
                    pa.field("previous_document_id", pa.string()),
                    pa.field("next_document_id", pa.string()),
                ]
            )
            self.rag_table = self.db.create_table(CONFIG.rag_table_name, schema=schema)

        # TODO: move this schema to a separate file. -- low priority.

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
            self.rag_table.search(query_embedding, vector_column_name="embedding")
            # .where(where_clause) # TODO: reintroduce this. -- high priority.
            .limit(CONFIG.vector_search_limit).to_list()
        )
        return results


db_utils = DBStore()
