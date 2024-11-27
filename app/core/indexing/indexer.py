import logging

logger = logging.getLogger(__name__)

from app.core.db_store.db_ops import db_utils
from app.core.parsing.parser import parser


class Indexer:
    def __init__(self):
        pass

    def index_document(self, document_path: str):
        documents = parser.parse_pdf_document(document_path)
        try:
            db_utils.store_documents(documents)
            logger.info(f"Indexed document: {document_path}")
        except Exception as e:
            logger.exception(f"Error in index_document: {e}")
            raise e


indexer = Indexer()
