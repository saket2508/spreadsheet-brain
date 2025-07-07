import { useState } from "react";
import { useUploadCsv, useQuerySpreadsheet } from "./hooks/useSpreadsheetApi";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const [query, setQuery] = useState("");

  const uploadMutation = useUploadCsv();
  const queryMutation = useQuerySpreadsheet();

  const handleFileSelect = (selectedFile: File | null) => {
    if (selectedFile && selectedFile.type === "text/csv") {
      setFile(selectedFile);
      uploadMutation.reset();
      queryMutation.reset();
    }
  };

  const handleUpload = () => {
    if (file) {
      uploadMutation.mutate(file);
    }
  };

  const handleSearch = () => {
    if (!query.trim() || !uploadMutation.data) return;
    queryMutation.mutate({ question: query, k: 5 });
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
                ? "border-blue-500 bg-blue-50"
                : "border-slate-300 hover:border-blue-400"
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
                <div className="text-4xl">{isDragOver ? "⬇️" : "📄"}</div>
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
                  {isDragOver ? "Drop your CSV file here" : "CSV files only"}
                </div>
              </div>
            </label>
          </div>

          {file && (
            <div className="mt-4">
              <button
                onClick={handleUpload}
                disabled={uploadMutation.isPending}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {uploadMutation.isPending ? (
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

          {uploadMutation.isError && (
            <div className="mt-4 p-3 rounded-lg text-sm bg-red-50 text-red-700 border border-red-200">
              ❌ Upload failed: {uploadMutation.error?.message}
            </div>
          )}

          {uploadMutation.isSuccess && uploadMutation.data && (
            <div className="mt-4 p-3 rounded-lg text-sm bg-green-50 text-green-700 border border-green-200">
              ✅ Successfully uploaded {uploadMutation.data.filename} (
              {uploadMutation.data.num_rows} rows,{" "}
              {uploadMutation.data.columns.length} columns)
            </div>
          )}
        </section>

        {/* Data Preview */}
        {uploadMutation.data && (
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
                  {uploadMutation.data.columns.join(", ")}
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-lg">
                <div className="text-sm text-slate-600">Total Rows</div>
                <div className="font-medium text-slate-900">
                  {uploadMutation.data.num_rows}
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-slate-200">
                    {uploadMutation.data.columns.map((col: string) => (
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
                  {uploadMutation.data.preview
                    .slice(0, 3)
                    .map(
                      (row: Record<string, string | number>, idx: number) => (
                        <tr key={idx} className="border-b border-slate-100">
                          {uploadMutation.data!.columns.map((col: string) => (
                            <td key={col} className="py-2 px-3 text-slate-700">
                              {row[col]}
                            </td>
                          ))}
                        </tr>
                      )
                    )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {/* Search Section */}
        {uploadMutation.data && (
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
                  !queryMutation.isPending &&
                  query.trim() &&
                  handleSearch()
                }
              />
              <button
                onClick={handleSearch}
                disabled={!query.trim() || queryMutation.isPending}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {queryMutation.isPending ? "Searching..." : "Search"}
              </button>
            </div>

            {queryMutation.isError && (
              <div className="mt-4 p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg text-sm">
                ❌ Query failed: {queryMutation.error?.message}
              </div>
            )}
          </section>
        )}

        {/* Results Section */}
        {queryMutation.data && (
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
                    {queryMutation.data.query_analysis.query_type}
                  </div>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Confidence:</span>
                  <div className="text-blue-900">
                    {(
                      queryMutation.data.query_analysis.confidence * 100
                    ).toFixed(1)}
                    %
                  </div>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Concepts:</span>
                  <div className="text-blue-900">
                    {queryMutation.data.query_analysis.extracted_concepts.join(
                      ", "
                    ) || "None"}
                  </div>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">Strategy:</span>
                  <div className="text-blue-900">
                    {queryMutation.data.query_analysis.search_strategy}
                  </div>
                </div>
              </div>
            </div>

            {/* Results */}
            <div>
              <h4 className="font-medium text-slate-900 mb-4">
                🎯 Found {queryMutation.data.total_results_found} relevant
                results
              </h4>
              <div className="space-y-4">
                {queryMutation.data.results.map((result, idx) => (
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
}

export default App;
