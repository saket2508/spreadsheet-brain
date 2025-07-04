from typing import Union

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

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
    if not file.filename.endswith(".csv"):
        return {"error": "Only CSV files are supported."}

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Preview first 5 rows as a list of dicts
    preview = df.head().to_dict(orient="records")

    return {
        "filename": file.filename,
        "num_rows": len(df),
        "columns": df.columns.tolist(),
        "preview": preview,
    }
