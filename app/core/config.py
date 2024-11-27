import os
from typing import NamedTuple


class Config(NamedTuple):
    chat_model: str
    lancedb_uri: str
    rag_table_name: str
    openai_key: str
    anthropic_api_key: str
    groq_api_key: str
    gemini_api_key: str
    default_embedding_model: str
    openai_embedding_model: str
    default_chat_model: str
    default_openai_chat_model: str
    default_anthropic_chat_model: str
    default_groq_chat_model: str
    huggingface_embedding_model: str
    retrieval_strategy: str
    vector_search_limit: int
    embedding_length: int
    database_type: str


def create_config_from_env(config_class):
    fields = {}
    for field in config_class._fields:
        value = os.getenv(field.upper())
        if value is None:
            raise ValueError(f"Missing environment variable: {field.upper()}")
        field_type = config_class.__annotations__[field]
        try:
            value = field_type(value) if value is not None else None
        except ValueError as e:
            raise ValueError(f"Invalid value for {field}: {value}") from e
        fields[field] = value
    return config_class(**fields)


CONFIG: Config = create_config_from_env(Config)
