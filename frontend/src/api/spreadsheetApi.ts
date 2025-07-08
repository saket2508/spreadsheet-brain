// API service functions for spreadsheet operations

export interface QueryResult {
  row_index: number;
  row_text: string;
  score: number;
  business_categories: string[];
  explanation: string;
  column_types: Record<string, string>;
  relevance_reason: string;
}

export interface QueryResponse {
  results: QueryResult[];
  query_analysis: {
    original_query: string;
    query_type: string;
    confidence: number;
    extracted_concepts: string[];
    search_strategy: string;
  };
  total_results_found: number;
}

export interface UploadResponse {
  filename: string;
  num_rows: number;
  columns: string[];
  preview: Record<string, string | number>[];
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Upload CSV file
export const uploadCsvFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Upload failed");
  }

  return response.json();
};

// Query spreadsheet data
export const querySpreadsheet = async ({
  question,
  k = 5,
}: {
  question: string;
  k?: number;
}): Promise<QueryResponse> => {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question, k }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || "Query failed");
  }

  return response.json();
};
