import logging
import uuid
from typing import Any, List

from app.core.db_store.db_schemas import Document
from app.core.ml.embedding_handler import embedding_handler

logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        pass

    def _get_headings(self, page: str) -> List[str]:
        import re

        headings = re.findall(r"^#+\s", page)
        return headings

    def _get_tables(self, page: str) -> str | None:
        import re

        table_pattern = r"(\|[^\n]*\|(?:\n\|[^\n]*\|)+)"
        match = re.search(table_pattern, page, re.DOTALL)
        if match:
            return match.group(0)
        else:
            return None

    def _get_images(self, page: str) -> List[str]:
        import re

        image_pattern = r"!\[.*?\]\((.*?)\)"
        matches = re.findall(image_pattern, page)
        return matches

    def _get_pages(self, md_text: str) -> List[Any]:
        import re

        pages = re.split(r"-----", md_text)
        return pages

    def _direct_parser(self, file_path: str) -> List[Any]:
        import pymupdf4llm

        md_text = pymupdf4llm.to_markdown(doc=file_path, embed_images=True)
        pages = self._get_pages(md_text)
        return pages

    def _get_image_description(self, images: List[str]) -> str:
        # TODO: add image description.
        return images[0]

    def _add_embeddings(self, documents: List[Document]) -> List[Document]:
        embeddings = [embedding_handler.embed_text(doc.text) for doc in documents]
        for i, doc in enumerate(documents):
            doc.embedding = embeddings[i]
        return documents

    def _embed_image(self, documents: List[Document]) -> List[Document]:
        embeddings = [
            embedding_handler.embed_image(doc.text.split(",")[1]) for doc in documents
        ]
        for i, doc in enumerate(documents):
            doc.embedding = embeddings[i]
        return documents

    def _embed_table(self, documents: List[Document]) -> List[Document]:
        embeddings = [embedding_handler.embed_table(doc.text) for doc in documents]
        for i, doc in enumerate(documents):
            doc.embedding = embeddings[i]
        return documents

    def parse_pdf_document(
        self, document_path: str, prase_strategy: str = "PAGE"
    ) -> List[Document]:
        """
        we assume parsing to be done a page level.

        - we may also do parsing at a sentence level.
        - an optional parameter parse_strategy would help in this.

        TODO: include a different parsing strategy.
        TODO: add keywords for hybrid fetch.
        """

        logger.info(f"Parsing document: {document_path}")
        parent_doc_id = str(uuid.uuid4()).replace("-", "")
        pages = self._direct_parser(document_path)
        logger.info(f"Found {len(pages)} pages")
        page_number_count = 1
        page_doc_id = None
        parsed_documents = []
        for page in pages:
            logger.info(f"Parsing page: {page_number_count}")
            headings = self._get_headings(page)
            page_number = page_number_count
            tables = self._get_tables(page)
            images = self._get_images(page)
            page_number_count += 1
            previous_page_doc_id = page_doc_id
            page_doc_id = str(uuid.uuid4()).replace("-", "")

            page_data = Document(
                id=page_doc_id,
                text=page,
                metadata={
                    "headings": headings,
                    "tables": True if tables else False,
                    "images": True if images else False,
                },
                parent_document_id=parent_doc_id,
                ref_in_parent=page_number,
                previous_document_id=previous_page_doc_id,
                type="PAGE",
            )
            logger.info(f"Parsed page: {page_number}")
            parsed_documents.append(page_data)
            if tables:
                table_data = Document(
                    id=str(uuid.uuid4()).replace("-", ""),
                    text=tables,
                    metadata={},
                    parent_document_id=page_doc_id,
                    ref_in_parent=page_number,
                    type="TABLE",
                )
                logger.info(f"Parsed *TABLE*: {page_number}")
                parsed_documents.append(table_data)
            if images:
                image_data = Document(
                    id=str(uuid.uuid4()).replace("-", ""),
                    text=self._get_image_description(images),
                    metadata={},
                    parent_document_id=page_doc_id,
                    ref_in_parent=page_number,
                    type="FIGURE",
                )
                logger.info(f"Parsed *IMAGE*: {page_number}")
                parsed_documents.append(image_data)
        parsed_documents = [
            (
                self._add_embeddings([doc])[0]
                if doc.type == "PAGE"
                else (
                    self._embed_image([doc])[0]
                    if doc.type == "FIGURE"
                    else self._embed_table([doc])[0] if doc.type == "TABLE" else doc
                )
            )
            for doc in parsed_documents
        ]
        # TODO: find how to embed other two types. image description will be fine, what about tables?
        return parsed_documents


parser = Parser()
