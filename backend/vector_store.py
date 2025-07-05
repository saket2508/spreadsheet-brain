from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")


def get_vectorstore(docs, persist_dir="./chroma_store"):
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    vectordb.persist()
    return vectordb


def load_vectorstore(persist_dir="./chroma_store"):
    return Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
