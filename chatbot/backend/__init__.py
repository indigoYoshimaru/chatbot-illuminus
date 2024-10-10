from langchain_community.chat_models import ChatOllama
from chatbot.backend.prompts import PromptController
from chatbot.backend.configs import ModelConfig, VectorDBConfig
from chatbot.backend.build_rag import build_db


prompt_controller = PromptController(prompt_dir="chatbot/prompts.yaml")
llm = ChatOllama(**ModelConfig().model_dump())
retriever = build_db(**VectorDBConfig().model_dump())
