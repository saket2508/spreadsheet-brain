from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class QueryRequest(BaseModel):
    question: str
    k: int = 5


class QueryResult(BaseModel):
    row_index: int
    row_text: str
    score: float
    business_categories: List[str]
    explanation: str
    column_types: Dict[str, str]
    relevance_reason: str


class QueryAnalysis(BaseModel):
    original_query: str
    query_type: str
    confidence: float
    extracted_concepts: List[str]
    search_strategy: str


class QueryResponse(BaseModel):
    results: List[QueryResult]
    query_analysis: QueryAnalysis
    total_results_found: int
