# 🧠 Spreadsheet Brain – Semantic Search for Spreadsheets

This project is a complete full-stack application built as part of a hiring assignment for Superjoin. It allows users to upload CSV files and query them using natural language through an intuitive web interface. The system performs semantic search to return the most relevant rows based on meaning, not just exact matches.

---

## 🚀 Features

- **Drag & Drop File Upload**: Intuitive CSV file upload with drag-and-drop support
- **Semantic Search**: Natural language queries with AI-powered understanding
- **Business Context Awareness**: Automatically categorizes data into business concepts
- **Column Type Detection**: Intelligent identification of data types (currency, percentage, categorical, etc.)
- **Query Analysis**: Detailed breakdown of query type, confidence, and search strategy
- **Real-time Results**: Instant semantic search with relevance scoring
- **Modern UI**: Clean, responsive interface built with TailwindCSS
- **API State Management**: Robust error handling and caching with TanStack Query

---

## 🧱 Tech Stack

### Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| API Server | FastAPI | REST API with automatic OpenAPI docs |
| AI Framework | LangChain | Embedding pipeline and document processing |
| Embeddings | OpenAI API | `text-embedding-3-small` model |
| Vector Store | ChromaDB | Local vector database for similarity search |
| Data Processing | Pandas | CSV parsing and data analysis |

### Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 19 | Modern React with hooks |
| Build Tool | Vite | Fast development and build |
| Styling | TailwindCSS | Utility-first CSS framework |
| State Management | TanStack Query | Server state, caching, and mutations |
| Type Safety | TypeScript | Static type checking |

---

## 📁 Project Structure

```
superjoin-hiring-assignment/
├── backend/
│   ├── main.py               # FastAPI app with CORS and endpoints
│   ├── utils.py              # CSV processing and business logic
│   ├── vector_store.py       # ChromaDB integration via LangChain
│   ├── models.py             # Pydantic request/response models
│   ├── requirements.txt      # Python dependencies
│   └── data/                 # Sample CSV files for testing
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React component
│   │   ├── main.tsx          # Entry point with QueryClient
│   │   ├── api/
│   │   │   └── spreadsheetApi.ts  # API service functions
│   │   └── hooks/
│   │       └── useSpreadsheetApi.ts  # TanStack Query hooks
│   ├── package.json          # Node.js dependencies
│   └── tailwind.config.js    # TailwindCSS configuration
├── .env                      # OpenAI API key
├── CLAUDE.md                 # AI assistant instructions
└── README.md
```

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- OpenAI API key

### 1. Clone the repository
```bash
git clone <repo-url>
cd superjoin-hiring-assignment
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file in the backend directory:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run the Application

**Backend** (Terminal 1):
```bash
cd backend
uvicorn main:app --reload
```

**Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

**Access the application**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## 📦 API Endpoints

### POST `/upload`
- **Purpose**: Upload and process CSV files
- **Input**: CSV file via multipart/form-data
- **Process**: Parses CSV → generates embeddings → stores in ChromaDB
- **Output**: File metadata, column info, and data preview

### POST `/query`
- **Purpose**: Semantic search through uploaded data
- **Input**: Natural language question and result count (k)
- **Process**: Analyzes query → performs vector similarity search
- **Output**: Ranked results with relevance scores and explanations

---

## 🧠 How It Works (Architecture)

### Data Processing Pipeline
1. **CSV Upload**: File is parsed using pandas with automatic column type detection
2. **Business Context**: Rows are categorized into business concepts (revenue, costs, ratios, etc.)
3. **Text Conversion**: Each row becomes a natural language description with metadata
4. **Embedding Generation**: OpenAI creates vector representations via LangChain
5. **Vector Storage**: ChromaDB stores embeddings with searchable metadata

### Query Processing
1. **Query Analysis**: Categorizes query type and extracts business concepts
2. **Semantic Search**: Vector similarity search in ChromaDB
3. **Result Ranking**: Relevance scoring with business context
4. **Response Generation**: Structured results with explanations

### Frontend Architecture
- **Component Structure**: Clean separation of concerns with custom hooks
- **State Management**: TanStack Query handles server state and caching
- **User Experience**: Drag-and-drop, loading states, and error handling
- **Type Safety**: Full TypeScript integration with proper interfaces

---

## ✅ Completed Features

- [x] **Backend Implementation**
  - [x] File upload with CSV parsing
  - [x] OpenAI embedding generation
  - [x] ChromaDB vector storage
  - [x] Semantic query processing
  - [x] Business context categorization
  - [x] Column type detection
  - [x] CORS configuration

- [x] **Frontend Implementation**
  - [x] React 19 with TypeScript
  - [x] TailwindCSS styling
  - [x] TanStack Query integration
  - [x] Drag & drop file upload
  - [x] Real-time search interface
  - [x] Results visualization
  - [x] Error handling and loading states

- [x] **Integration & Testing**
  - [x] End-to-end data flow
  - [x] Multiple CSV format support
  - [x] Query analysis and explanations
  - [x] Production-ready error handling

---

## 🧪 Example Usage

### Sample CSV Files
The project includes test CSV files in `backend/data/`:
- `pl_statement.csv` - Profit & Loss statement
- `finance_ratios.csv` - Financial ratios
- `cost_analysis.csv` - Cost breakdown
- `3_year_forecast.csv` - Multi-year projections
- `dashboard.csv` - Business dashboard data

### Example Queries
- "What is the total revenue?"
- "Show me all profitability metrics"
- "Find operational costs"
- "Where are efficiency ratios?"
- "Show percentage calculations"

---

## 🚀 Development Commands

### Backend
```bash
# Start development server
uvicorn main:app --reload

# View API documentation
open http://localhost:8000/docs
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

---

## 🔧 Technical Details

### Vector Store Configuration
- **Model**: OpenAI `text-embedding-3-small`
- **Dimensions**: 1536
- **Storage**: Local ChromaDB instance
- **Metadata**: Business categories, column types, formulas

### Query Processing
- **Analysis**: Query type classification with confidence scoring
- **Search Strategy**: Semantic similarity with business context
- **Ranking**: Relevance scoring with explanations

### Frontend Features
- **Responsive Design**: Mobile-first approach with TailwindCSS
- **Performance**: Optimized with React 19 and Vite
- **Developer Experience**: TypeScript, ESLint, and hot reload

---

## 📜 License

MIT

---

## 🙌 Author

**Saket S Narayan**  
Frontend/Full-Stack Developer  
https://github.com/saket2508