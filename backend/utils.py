import pandas as pd


def dataframe_to_documents(df):
    from langchain.schema import Document

    docs = []
    for i, row in df.iterrows():
        row_text = ", ".join(
            [f"{col}: {row[col]}" for col in df.columns if pd.notnull(row[col])])
        docs.append(Document(page_content=row_text, metadata={"row_index": i}))
    return docs
