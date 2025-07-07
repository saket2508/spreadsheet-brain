
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from models import QueryRequest

import pandas as pd
import io
from dotenv import load_dotenv
from vector_store import get_vectorstore, load_vectorstore
from utils import dataframe_to_documents
from query_processor import QueryProcessor
# from tagging import explain_classification  # Currently unused
load_dotenv()  # Loads .env variables into os.environ


app = FastAPI()

# Initialize query processor
query_processor = QueryProcessor()

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_spreadsheet(query: QueryRequest):
    try:
        vectordb = load_vectorstore()  # reload persisted Chroma index

        # Process query using intelligent query understanding
        query_analysis = query_processor.process_query(query.question)

        # Get initial results with expanded search terms
        all_results = []
        search_terms = [query.question] + \
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
                    doc_categories = eval(
                        categories_json) if categories_json else []
                except:
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
                categories = eval(metadata.get('categories_json', '[]'))
            except:
                categories = []

            try:
                column_types = eval(metadata.get('column_types_json', '{}'))
            except:
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
                "relevance_reason": _explain_relevance(query_analysis, categories, doc.page_content)
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


def _explain_relevance(query_analysis, doc_categories, doc_content):
    """Generate explanation for why this result is relevant to the query."""
    extracted_concepts = query_analysis.get('extracted_concepts', [])
    query_type = query_analysis.get('categorization', {}).get(
        'primary_category', 'unknown')

    # Find matching concepts
    matching_concepts = [
        concept for concept in extracted_concepts if concept in doc_categories]

    if matching_concepts:
        return f"Matches {', '.join(matching_concepts)} concepts from your {query_type} query"
    elif doc_categories:
        return f"Contains {', '.join(doc_categories[:2])} data relevant to your search"
    else:
        # Use doc_content for basic text similarity explanation
        return f"Text similarity match with your query (content: {doc_content[:50]}...)"


@app.get("/")
async def root():
    return {"message": "Semantic Search Engine for Spreadsheets - Ready"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "features": {
            "semantic_search": True,
            "query_categorization": True,
            "business_understanding": True,
            "enhanced_metadata": True
        }
    }
