from core.db_store.db_ops import db_utils
from crewai.tools import BaseTool


class FetchDocsTool(BaseTool):
    name = "Senior SQL Query Maker"
    description = "You are an expert in writing SQL queries, your task is to fill in necessary fields which will be part of an SQL query that fetches information regarding a given question."

    def _run(self, query: str):
        return db_utils.get_documents(query)
