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
            collection_name="embeddings",
            embedding=NomicEmbeddings(
                model=embedding_model,
                inference_mode="local",
            ),
            persist_directory="./chroma_db",
        )
        vectorstore.persist()
    except Exception as e:
        logger.error(f"{type(e).__name__}: {e}")
        raise e
    else:
        retriever = vectorstore.as_retriever()
        return retriever
