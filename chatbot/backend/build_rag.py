from typing import Text
from loguru import logger
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever


def build_db(
    data_directory: Text,
    embedding_model: Text,
) -> VectorStoreRetriever:
    try:
        import glob

        docs = glob.glob(f"{data_directory}/*.txt")
        assert docs, "No .txt document found"
        # docs_list = []
        # for doc in docs:
        #     docs_list += TextLoader(doc).load()
        docs = [TextLoader(doc).load() for doc in docs]
        docs_list = [item for sublist in docs for item in sublist]

        assert docs_list, f"Cannot perform text loading of documents {docs}"
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        raise e
    else:
        logger.success(f"Successfully load text from {docs_list}")

    try:
        logger.info(f"Adding text to vectorstore...")
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=600,
            chunk_overlap=0,
        )
        doc_splits = text_splitter.split_documents(docs_list)
        vectorstore = Chroma.from_documents(
            documents=doc_splits,
            collection_name="rag-chroma",
            embedding=NomicEmbeddings(
                model=embedding_model,
                inference_mode="local",
            ),
        )
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        raise e
    else:
        retriever = vectorstore.as_retriever()
        return retriever


if __name__ == "__main__":
    from langchain_community.chat_models import ChatOllama
    from chatbot.backend.prompts import PromptController

    local_model = "llama3.2"
    llm = ChatOllama(model=local_model, temperature=0.5)
    # question = "나는 정치에 대해 유머러스한 견해를 갖고 싶다."
    question_list = [
        "What's your name?",
        "I want a humorous take on politics.",
        "나는 정치에 대해 유머러스한 견해를 갖고 싶다.",
        'how to play "which one is it"?',
        '"어느 것이야?" 게임하는 방법?',
    ]

    prompt_controller = PromptController(prompt_dir="chatbot/prompts.yaml")

    retriever = build_db("data", "nomic-embed-text-v1.5")
    template = prompt_controller.translation
    generator = prompt_controller.researcher | llm
    print(generator)
    for question in question_list:
        print(question)
        docs = retriever.invoke(question)
        print(docs)
        # doc_txt = docs[0].page_content
        generation = generator.invoke({"document": docs, "question": question})
        # p_template = template.invoke(
        #     {"in_lang": "English", "out_lang": "Korean", "input": question}
        # )
        # print(p_template.to_string())
        # generation = llm.invoke(p_template.to_string())
        print(generation.content)
