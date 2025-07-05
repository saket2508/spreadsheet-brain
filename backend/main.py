
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import QueryRequest

import pandas as pd
import io
from dotenv import load_dotenv
from vector_store import get_vectorstore, load_vectorstore
from utils import dataframe_to_documents
load_dotenv()  # Loads .env variables into os.environ


app = FastAPI()

# TODO:Enable CORS if you're calling from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=400, detail="Only CSV files are supported.")

        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        # Create searchable documents
        docs = dataframe_to_documents(df)

        # Create vector store
        get_vectorstore(docs)

        # Preview first 5 rows as a list of dicts
        preview = df.head().to_dict(orient="records")

        return {
            "filename": file.filename,
            "num_rows": len(df),
            "columns": df.columns.tolist(),
            "preview": preview,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_spreadsheet(query: QueryRequest):
    try:
        vectordb = load_vectorstore()  # reload persisted Chroma index
        results = vectordb.similarity_search_with_score(
            query.question, k=query.k)

        response = []
        for doc, score in results:
            response.append({
                "row_index": doc.metadata.get("row_index"),
                "row_text": doc.page_content,
                "score": round(score, 3)
            })

        return {"results": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello World"}
