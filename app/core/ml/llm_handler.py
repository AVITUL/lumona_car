import logging
from typing import Any, Type

from langchain.output_parsers import PydanticOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from app.core.config import CONFIG


class LLMCaller:
    def __init__(self):
        self.chat_model = None
        try:
            if CONFIG.default_chat_model == "openai":
                self.chat_model = ChatOpenAI(
                    model="gpt-4o",  # TODO: check why we are not able to parse from config file? for this part? -- high priority.
                    temperature=0.1,
                    api_key=CONFIG.openai_key,  # type: ignore
                )
            elif CONFIG.default_chat_model == "anthropic":
                self.chat_model = ChatAnthropic(
                    model_name=CONFIG.default_anthropic_chat_model,
                    timeout=10,
                    api_key=CONFIG.anthropic_api_key,  # type: ignore
                )
            elif CONFIG.default_chat_model == "groq":
                self.chat_model = ChatGroq(
                    model=CONFIG.default_groq_chat_model,
                    temperature=0.1,
                    api_key=CONFIG.groq_api_key,  # type: ignore
                )
        except Exception as e:
            logger.error(f"Error initializing chat model: {e}")
            raise e

    # add retry
    def generate_structured_response(
        self, output_schema: Type[BaseModel], system_prompt: str, **kwargs
    ) -> Any:
        try:
            system_prompt = SystemMessagePromptTemplate.from_template(
                system_prompt
            ).format(
                **kwargs
            )  # type: ignore
            if not self.chat_model:
                self.chat_model = ChatOpenAI(
                    model="gpt-4o", api_key=CONFIG.openai_key  # type: ignore
                )
            chat_model_with_struct = self.chat_model.with_structured_output(
                schema=output_schema, method="json_mode"
            )
            query = chat_model_with_struct.invoke([system_prompt])
            return query
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            raise e

    # TODO: test with other models in api mode.

    def get_image_description(self, image_data: str) -> str:
        model = ChatOpenAI(model="gpt-4o", api_key=CONFIG.openai_key)  # type: ignore
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": " the image you see is taken from a car manual. it may include instructions, car part labels, or some view of a description. in any case, give a short description of the content. if there is text written such as labels, add them in the end in a list of strings. if no text or labels are present, do not mention anything about them.  ",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                },
            ]
        )
        response = model.invoke([message])
        return str(response.content)

    def get_table_description(self, table: str) -> str:
        model = ChatOpenAI(model="gpt-4o", api_key=CONFIG.openai_key)  # type: ignore
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": f"the following table is taken from a car manual. it may contain comparision of different models, or a list of components, or care instructions. we want an overview of the table, that does not state exact information contained in the table but a high level description of the content which will help us in getting a summarised view of the table. we will use this information to decide if we want to dive deeper into the information contained in the table.: {table}",
                }
            ]
        )
        response = model.invoke([message])
        return str(response.content)


llm_caller = LLMCaller()
