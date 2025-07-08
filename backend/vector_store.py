from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")


def get_vectorstore(docs, persist_dir="./chroma_store"):
    try:
        print(f"Getting vectorstore for {len(docs)} documents")
        vectordb = Chroma.from_documents(
            documents=docs,
            embedding=embedding_model,
            persist_directory=persist_dir
        )
        vectordb.persist()
        return vectordb
    except Exception as e:
        print(f"Error getting vectorstore: {e}")
        raise e


def load_vectorstore(persist_dir="./chroma_store"):
    try:
        return Chroma(
            persist_directory=persist_dir, embedding_function=embedding_model
        )
    except Exception as e:
        print(f"Error loading vectorstore: {e}")
        raise e
