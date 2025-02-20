from pydantic import BaseModel
from typing import Text


class ModelConfig(BaseModel):
    model: Text = "llama3.2"
    temperature: float = 0.1


class VectorDBConfig(BaseModel):
    data_directory: Text = "data"
    embedding_model: Text = "nomic-embed-text-v1.5"
