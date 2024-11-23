from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic.v1 import BaseModel
from typing import Type
import logging
logger = logging.getLogger(__name__)

from core.config import CONFIG

class LLMCaller:
    def __init__(self):
        self.model = CONFIG.chat_model
        self.openai_key = CONFIG.openai_key
        self.openai_client = OpenAI(api_key=self.openai_key)
        self.chat_model = ChatOpenAI(
            model=self.model,
            temperature=0.1,
            api_key=self.openai_key # type: ignore
        )

    # TODO: revisit this entire file. 
    def generate_structured_response(self, output_schema: Type[BaseModel], system_prompt: str, **kwargs) -> BaseModel:
        try:
            parser = PydanticOutputParser(pydantic_object=output_schema)
            model = self.chat_model.with_structured_outputs(output_schema, method="json_mode")
            query = model.invoke(
                [SystemMessagePromptTemplate.from_template(system_prompt).format(format_instructions=parser.get_format_instructions(), **kwargs)]
            )
            return query
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            raise e 
        


llm_caller = LLMCaller()
