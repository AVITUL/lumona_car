import logging

from pymongo.mongo_client import MongoClient
from pymongo.operations import SearchIndexModel

from app.core.config import CONFIG
from app.core.db_store.db_schemas import CarSchema, Document

logger = logging.getLogger(__name__)

# only works on the paid version of MongoDB. -- https://stackoverflow.com/questions/78104428/create-search-index-fails-with-motor-pymongo-on-mongodb-6-0-14-on-atlas-free-ti


class DBMongo:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["lumona_car"]
        self.documents_collection = self.db["documents"]
        self.cars_collection = self.db["cars"]

        existing_indexes = self.documents_collection.list_indexes()
        vector_index_exists = any(
            index["name"] == "vector_search_index" for index in existing_indexes
        )
        if not vector_index_exists:
            dummy_entry = Document(
                id="dummy",
                text="dummy",
                type="TABLE",
                metadata={},
            )
            self.insert_document(dummy_entry)
            self.vector_search_index = SearchIndexModel(
                definition={
                    "fields": [
                        {
                            "type": "vector",
                            "numDimensions": CONFIG.embedding_length,
                            "path": "embedding",
                            "similarity": "cosine",
                        }
                    ]
                },
                name="vector_search_index",  # move this name to constants.py
                type="vectorSearch",
            )
            search_index_creation_progress = (
                self.documents_collection.create_search_index(self.vector_search_index)
            )
            logger.info(
                f"Vector search index creation progress: {search_index_creation_progress}"
            )
            self.documents_collection.delete_one({"id": "dummy"})

    def insert_document(self, document: Document):
        self.documents_collection.insert_one(document.model_dump())

    def insert_car(self, car: CarSchema):
        self.cars_collection.insert_one(car.model_dump())

    def get_documents_with_vector_search(
        self, query_embedding: list[float]
    ) -> list[dict]:
        search_pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_search_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": CONFIG.vector_search_limit,
                    # "indexType": "hnsw",
                    "similarity": "cosine",
                }
            },
            {
                "$project": {
                    "id": 1,
                    "text": 1,
                    "type": 1,
                }
            },
        ]
        cursor = self.documents_collection.aggregate(search_pipeline)
        return [i for i in cursor]


db_mongo = DBMongo()
