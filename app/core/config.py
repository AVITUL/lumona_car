import os 

from typing import NamedTuple

class Config(NamedTuple):
    chat_model: str
    lancedb_uri: str 
    rag_table_name: str
    openai_key: str 
    gemini_api_key: str


def create_config_from_env_file(config_class):
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

CONFIG: Config = create_config_from_env_file(Config)
