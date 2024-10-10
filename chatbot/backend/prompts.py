from pydantic import BaseModel
from typing import Text
from langchain_core.prompts import PromptTemplate


class PromptController(BaseModel):
    son: PromptTemplate
    researcher: PromptTemplate
    comedian: PromptTemplate
    speaker: PromptTemplate
    translation: PromptTemplate
    role_detector: PromptTemplate

    def __init__(self, prompt_dir: Text):
        from chatbot.utils import fileio

        file_reader = fileio.FileReader()
        prompt_dict = file_reader.read(prompt_dir)
        for k, v in prompt_dict.items():
            prompt_dict[k] = PromptTemplate(
                **v,
            )
        super().__init__(**prompt_dict)
