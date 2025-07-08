
from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from models import QueryRequest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import pandas as pd
import io
import json
from dotenv import load_dotenv
from vector_store import get_vectorstore, load_vectorstore
from utils import dataframe_to_documents, validate_csv_file, explain_relevance, sanitize_query_input
from query_processor import QueryProcessor
# from tagging import explain_classification  # Currently unused
load_dotenv()  # Loads .env variables into os.environ


app = FastAPI()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize query processor
query_processor = QueryProcessor()

# CORS configuration for secure cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Local development (Vite)
        "http://localhost:3000",      # Local development (alternative)
        "https://superjoin-hiring-frontend-saket.vercel.app",  # Production Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.post("/upload")
@limiter.limit("8/hour")  # 8 uploads per hour per IP
async def upload_csv(request: Request, file: UploadFile = File(...)):
    try:
        # File validation
        await validate_csv_file(file)

        contents = await file.read()
        print(f"Uploading file: {file.filename}")

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
    except HTTPException:
        raise  # Re-raise HTTP exceptions (like validation errors)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
@limiter.limit("30/minute")  # 30 queries per minute per IP
async def query_spreadsheet(request: Request, query: QueryRequest):
    try:
        # Sanitize query input for security
        sanitized_question = sanitize_query_input(query.question)

        vectordb = load_vectorstore()  # reload persisted Chroma index

        # Process query using intelligent query understanding
        query_analysis = query_processor.process_query(sanitized_question)

        # Get initial results with expanded search terms
        all_results = []
        search_terms = [sanitized_question] + \
            query_analysis.get('expanded_terms', [])

        # Search with original query and expanded terms
        # Limit to avoid too many searches
        for search_term in search_terms[:3]:
            results = vectordb.similarity_search_with_score(
                search_term, k=query.k * 2)
            all_results.extend(results)

        # Remove duplicates based on row_index
        unique_results = {}
        for doc, score in all_results:
            row_index = doc.metadata.get("row_index")
            if row_index not in unique_results or score < unique_results[row_index][1]:
                unique_results[row_index] = (doc, score)

        # Convert back to list and sort by score
        filtered_results = list(unique_results.values())
        # Sort by score (lower is better)
        filtered_results.sort(key=lambda x: x[1])

        # Apply category-based filtering if applicable
        processing_result = query_analysis.get('processing_result', {})
        filter_categories = processing_result.get('filter_categories', [])

        if filter_categories:
            # Filter results based on business categories
            category_filtered = []
            for doc, score in filtered_results:
                # Parse JSON string back to list for categories
                categories_json = doc.metadata.get('categories_json', '[]')
                try:
                    doc_categories = json.loads(
                        categories_json) if categories_json else []
                except (json.JSONDecodeError, TypeError):
                    doc_categories = []

                if any(cat in doc_categories for cat in filter_categories):
                    category_filtered.append((doc, score))

            # If category filtering returns results, use them; otherwise fall back to all results
            if category_filtered:
                filtered_results = category_filtered

        # Limit to requested number of results
        final_results = filtered_results[:query.k]

        # Format enhanced response
        response = []
        for doc, score in final_results:
            metadata = doc.metadata

            # Parse JSON metadata back to objects
            try:
                categories = json.loads(metadata.get('categories_json', '[]'))
            except (json.JSONDecodeError, TypeError):
                categories = []

            try:
                column_types = json.loads(
                    metadata.get('column_types_json', '{}'))
            except (json.JSONDecodeError, TypeError):
                column_types = {}

            classification_explanation = metadata.get(
                'classification_explanation', '')

            response.append({
                "row_index": metadata.get("row_index"),
                "row_text": doc.page_content,
                "score": round(score, 3),
                "business_categories": categories,
                "explanation": classification_explanation,
                "column_types": column_types,
                "relevance_reason": explain_relevance(query_analysis, categories, doc.page_content)
            })

        return {
            "results": response,
            "query_analysis": {
                "original_query": query.question,
                "query_type": query_analysis.get('categorization', {}).get('primary_category', 'unknown'),
                "confidence": query_analysis.get('categorization', {}).get('confidence', 0),
                "extracted_concepts": query_analysis.get('extracted_concepts', []),
                "search_strategy": processing_result.get('search_strategy', 'semantic_similarity')
            },
            "total_results_found": len(response)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
@limiter.limit("10/minute")  # Basic rate limit for root endpoint
async def root(request: Request):
    return {"message": "Semantic Search Engine for Spreadsheets - Ready"}


@app.get("/health")
@limiter.limit("20/minute")  # Health checks can be more frequent
async def health_check(request: Request):
    return {
        "status": "healthy",
        "features": {
            "semantic_search": True,
            "query_categorization": True,
            "business_understanding": True,
            "enhanced_metadata": True
        }
    }
