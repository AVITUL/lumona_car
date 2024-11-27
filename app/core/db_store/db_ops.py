import logging

import lancedb
import pyarrow as pa

from app.core.config import CONFIG
from app.core.db_store.db_schemas import Document

logger = logging.getLogger(__name__)


class DBStore:
    def __init__(self):
        self.uri = CONFIG.lancedb_uri
        self.db = lancedb.connect(self.uri)
        logger.info(f"Connected to LanceDB at {self.uri}")

        if CONFIG.rag_table_name in self.db.table_names():
            self.rag_table = self.db.open_table(CONFIG.rag_table_name)
            logger.info(f"Opened table {CONFIG.rag_table_name}")

        else:
            logger.info(f"Table not found, creating one: {CONFIG.rag_table_name}")
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
            logger.info(f"Created table {CONFIG.rag_table_name}")

        # TODO: move this schema to a separate file. -- low priority.

    def store_documents(self, documents: list[Document]):
        try:
            documents_in_dict = [item.model_dump() for item in documents]
            if CONFIG.rag_table_name not in self.db.table_names():
                self.rag_table = self.db.create_table(
                    CONFIG.rag_table_name, data=documents_in_dict
                )
                logger.info(f"Created table {CONFIG.rag_table_name}")
            else:
                self.rag_table.add(documents_in_dict)
                logger.info(
                    f"Added {len(documents)} documents to table {CONFIG.rag_table_name}"
                )
        except Exception as e:
            logger.exception(f"Error in store_documents: {e}")
            raise e

    def get_documents(self, query: str):
        try:
            rag_table = self.db.open_table(CONFIG.rag_table_name)
            results = rag_table.search(query).limit(10).to_list()
            logger.info(f"Got {len(results)} results for query")
            return results
        except Exception as e:
            logger.exception(f"Error in get_documents: {e}")
            raise e

    def vector_search(self, query_embedding: list[float], where_clause: str = ""):
        try:
            results = (
                self.rag_table.search(query_embedding, vector_column_name="embedding")
                # .where(where_clause)  # TODO: reintroduce this. -- high priority.
                .limit(CONFIG.vector_search_limit).to_list()
            )
            return results
        except Exception as e:
            logger.exception(f"Error in vector_search: {e}")
            raise e

    def get_document_by_ref(self, ref: str):
        try:
            return (
                self.rag_table.search()
                .where(f"id == '{ref}'")
                .select(["text"])
                .to_list()
            )
        except Exception as e:
            logger.exception(f"Error in get_document_by_ref: {e}")
            raise e


db_utils = DBStore()
