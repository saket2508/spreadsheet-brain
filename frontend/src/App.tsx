import { useState } from "react";
interface QueryResult {
  row_index: number;
  row_text: string;
  score: number;
  business_categories: string[];
  explanation: string;
  column_types: Record<string, string>;
  relevance_reason: string;
}

interface QueryResponse {
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

interface UploadResponse {
  filename: string;
  num_rows: number;
  columns: string[];
  preview: Record<string, string | number>[];
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [uploadedData, setUploadedData] = useState<UploadResponse | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const [query, setQuery] = useState("");
  const [isQuerying, setIsQuerying] = useState(false);
  const [queryResults, setQueryResults] = useState<QueryResponse | null>(null);
  const [queryError, setQueryError] = useState<string>("");

  // File handling functions
  const handleFileSelect = (selectedFile: File | null) => {
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setUploadStatus('');
      setUploadedData(null);
      setQueryResults(null);
    } else if (selectedFile) {
      setUploadStatus('❌ Please select a CSV file only');
    }
  };

  // Drag and drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      handleFileSelect(droppedFiles[0]);
    }
  };

  const exampleQueries = [
    "What is the total revenue?",
    "Show me all profitability metrics",
    "Find operational costs",
    "Where are efficiency ratios?",
    "Show percentage calculations",
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-xl font-bold">🧠</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">
                Spreadsheet Brain
              </h1>
              <p className="text-slate-600 text-sm">
                Semantic Search Engine for Spreadsheets
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <h2 className="text-4xl font-bold text-slate-900">
            Ask questions about your spreadsheet data
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Upload your CSV files and search using natural language. Our AI
            understands business concepts, formulas, and relationships in your
            data.
          </p>
        </div>

        {/* File Upload Section */}
        <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center space-x-2 mb-4">
            <span className="text-blue-500">📁</span>
            <h3 className="text-lg font-semibold text-slate-900">
              Upload Spreadsheet
            </h3>
          </div>

          <div 
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-slate-300 hover:border-blue-400'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".csv"
              onChange={(e) => handleFileSelect(e.target.files?.[0] || null)}
              className="hidden"
              id="file-input"
            />
            <label htmlFor="file-input" className="cursor-pointer block">
              <div className="space-y-2">
                <div className="text-4xl">
                  {isDragOver ? '⬇️' : '📄'}
                </div>
                <div className="text-slate-600">
                  {file ? (
                    <span className="font-medium text-slate-900">
                      {file.name}
                    </span>
                  ) : (
                    <>
                      <span className="font-medium text-blue-600">
                        Click to upload
                      </span>{" "}
                      or drag and drop
                    </>
                  )}
                </div>
                <div className="text-sm text-slate-500">
                  {isDragOver ? 'Drop your CSV file here' : 'CSV files only'}
                </div>
              </div>
            </label>
          </div>

          {file && (
            <div className="mt-4">
              <button
                onClick={async () => {
                  if (!file) return;

                  setIsUploading(true);
                  setUploadStatus("");

                  const formData = new FormData();
                  formData.append("file", file);

                  try {
                    const response = await fetch(
                      "http://localhost:8000/upload",
                      {
                        method: "POST",
                        body: formData,
                      }
                    );

                    if (response.ok) {
                      const data: UploadResponse = await response.json();
                      setUploadedData(data);
                      setUploadStatus(
                        `✅ Successfully uploaded ${data.filename} (${data.num_rows} rows, ${data.columns.length} columns)`
                      );
                    } else {
                      const errorData = await response.json();
                      setUploadStatus(
                        `❌ Upload failed: ${
                          errorData.detail || "Unknown error"
                        }`
                      );
                    }
                  } catch (error) {
                    setUploadStatus(
                      `❌ Upload failed: ${
                        error instanceof Error ? error.message : "Network error"
                      }`
                    );
                  } finally {
                    setIsUploading(false);
                  }
                }}
                disabled={isUploading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isUploading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Processing...</span>
                  </div>
                ) : (
                  "Upload & Process"
                )}
              </button>
            </div>
          )}

          {uploadStatus && (
            <div
              className={`mt-4 p-3 rounded-lg text-sm ${
                uploadStatus.includes("❌")
                  ? "bg-red-50 text-red-700 border border-red-200"
                  : "bg-green-50 text-green-700 border border-green-200"
              }`}
            >
              {uploadStatus}
            </div>
          )}
        </section>

        {/* Data Preview */}
        {uploadedData && (
          <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-green-500">📊</span>
              <h3 className="text-lg font-semibold text-slate-900">
                Data Preview
              </h3>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-slate-50 p-3 rounded-lg">
                <div className="text-sm text-slate-600">Columns</div>
                <div className="font-medium text-slate-900">
                  {uploadedData.columns.join(", ")}
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-lg">
                <div className="text-sm text-slate-600">Total Rows</div>
                <div className="font-medium text-slate-900">
                  {uploadedData.num_rows}
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-slate-200">
                    {uploadedData.columns.map((col) => (
                      <th
                        key={col}
                        className="text-left py-2 px-3 font-medium text-slate-900 bg-slate-50"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {uploadedData.preview.slice(0, 3).map((row, idx) => (
                    <tr key={idx} className="border-b border-slate-100">
                      {uploadedData.columns.map((col) => (
                        <td key={col} className="py-2 px-3 text-slate-700">
                          {row[col]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Search Section */}
        {uploadedData && (
          <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <span className="text-purple-500">🔍</span>
              <h3 className="text-lg font-semibold text-slate-900">
                Semantic Search
              </h3>
            </div>

            {/* Example Queries */}
            <div className="mb-6">
              <p className="text-sm text-slate-600 mb-3">
                Try these example queries:
              </p>
              <div className="flex flex-wrap gap-2">
                {exampleQueries.map((exampleQuery, idx) => (
                  <button
                    key={idx}
                    onClick={() => setQuery(exampleQuery)}
                    className="px-3 py-2 bg-slate-100 text-slate-700 text-sm rounded-lg hover:bg-slate-200 transition-colors"
                  >
                    {exampleQuery}
                  </button>
                ))}
              </div>
            </div>

            {/* Search Input */}
            <div className="flex space-x-2">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a natural language question about your spreadsheet..."
                className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                onKeyDown={(e) =>
                  e.key === "Enter" &&
                  !isQuerying &&
                  query.trim() &&
                  handleSearch()
                }
              />
              <button
                onClick={handleSearch}
                disabled={!query.trim() || isQuerying}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isQuerying ? "Searching..." : "Search"}
              </button>
            </div>

            {queryError && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm">
                ❌ {queryError}
              </div>
            )}
          </section>
        )}

        {/* Results Section */}
        {queryResults && (
          <section className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center space-x-2 mb-6">
              <span className="text-green-500">📈</span>
              <h3 className="text-lg font-semibold text-slate-900">
                Search Results
              </h3>
            </div>

            {/* Query Analysis */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h4 className="font-medium text-blue-900 mb-2">
                🔬 Query Analysis
              </h4>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-blue-600 font-medium">Type:</span>
                  <div className="text-blue-900">
                    {queryResults.query_analysis.query_type}
                  </div>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Confidence:</span>
                  <div className="text-blue-900">
                    {(queryResults.query_analysis.confidence * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Concepts:</span>
                  <div className="text-blue-900">
                    {queryResults.query_analysis.extracted_concepts.join(
                      ", "
                    ) || "None"}
                  </div>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Strategy:</span>
                  <div className="text-blue-900">
                    {queryResults.query_analysis.search_strategy}
                  </div>
                </div>
              </div>
            </div>

            {/* Results */}
            <div>
              <h4 className="font-medium text-slate-900 mb-4">
                🎯 Found {queryResults.total_results_found} relevant results
              </h4>
              <div className="space-y-4">
                {queryResults.results.map((result, idx) => (
                  <div
                    key={idx}
                    className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="bg-blue-100 text-blue-800 text-sm font-medium px-2 py-1 rounded">
                        #{idx + 1}
                      </span>
                      <span className="text-sm text-slate-600">
                        Relevance: {(1 - result.score).toFixed(3)}
                      </span>
                    </div>

                    <div className="mb-3">
                      <p className="text-slate-900 font-medium">
                        {result.row_text}
                      </p>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium text-slate-700">
                          Business Categories:
                        </span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {result.business_categories.map((cat, catIdx) => (
                            <span
                              key={catIdx}
                              className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs"
                            >
                              {cat}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <span className="font-medium text-slate-700">
                          Column Types:
                        </span>
                        <span className="ml-2 text-slate-600">
                          {Object.entries(result.column_types)
                            .map(([col, type]) => `${col}: ${type}`)
                            .join(", ")}
                        </span>
                      </div>

                      <div>
                        <span className="font-medium text-slate-700">
                          Why this matches:
                        </span>
                        <span className="ml-2 text-slate-600">
                          {result.relevance_reason}
                        </span>
                      </div>

                      <div>
                        <span className="font-medium text-slate-700">
                          Explanation:
                        </span>
                        <span className="ml-2 text-slate-600">
                          {result.explanation}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );

  // Helper function for search
  async function handleSearch() {
    if (!query.trim() || !uploadedData) return;

    setIsQuerying(true);
    setQueryError("");

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: query,
          k: 5,
        }),
      });

      if (response.ok) {
        const data: QueryResponse = await response.json();
        setQueryResults(data);
      } else {
        const errorData = await response.json();
        setQueryError(`Query failed: ${errorData.detail || "Unknown error"}`);
      }
    } catch (error) {
      setQueryError(
        `Query failed: ${
          error instanceof Error ? error.message : "Network error"
        }`
      );
    } finally {
      setIsQuerying(false);
    }
  }
}

export default App;
