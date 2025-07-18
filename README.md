# 🧠 Spreadsheet Brain – Semantic Search for Spreadsheets

> **🌐 [Live Demo](https://superjoin-hiring-frontend-saket.vercel.app)** - Try the application now!

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

| Component       | Technology | Purpose                                     |
| --------------- | ---------- | ------------------------------------------- |
| API Server      | FastAPI    | REST API with automatic OpenAPI docs        |
| AI Framework    | LangChain  | Embedding pipeline and document processing  |
| Embeddings      | OpenAI API | `text-embedding-3-small` model              |
| Vector Store    | ChromaDB   | Local vector database for similarity search |
| Data Processing | Pandas     | CSV parsing and data analysis               |

### Frontend

| Component        | Technology     | Purpose                              |
| ---------------- | -------------- | ------------------------------------ |
| Framework        | React 19       | Modern React with hooks              |
| Build Tool       | Vite           | Fast development and build           |
| Styling          | TailwindCSS    | Utility-first CSS framework          |
| State Management | TanStack Query | Server state, caching, and mutations |
| Type Safety      | TypeScript     | Static type checking                 |

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

#### Option A: Running Locally

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

#### Option B: Running with Docker

**Prerequisites**: Docker and Docker Compose installed

1. **Configure environment variables**:

   ```bash
   cd backend
   echo "OPENAI_API_KEY=sk-your-actual-openai-api-key-here" > .env
   cd ..
   ```

2. **Build and run containers**:

   ```bash
   # Build Docker images
   docker-compose build

   # Start services in detached mode
   docker-compose up -d

   # Check service status
   docker-compose ps
   ```

3. **Access the containerized application**:

   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

4. **Management commands**:

   ```bash
   # View logs
   docker-compose logs -f

   # View specific service logs
   docker-compose logs -f backend
   docker-compose logs -f frontend

   # Stop services
   docker-compose down

   # Stop and remove volumes
   docker-compose down -v
   ```

**Docker Architecture**:

- **Backend**: FastAPI container with ChromaDB persistence
- **Frontend**: Multi-stage build (Node.js → Nginx) with API proxy
- **Networking**: Internal Docker network for service communication
- **Volumes**: ChromaDB data persists across container restarts

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

## 🚀 Production Deployment

### Deployment Architecture

- **Backend**: Railway (with volume persistence)
- **Frontend**: Vercel (with global CDN)
- **Database**: ChromaDB on Railway volume
- **Security**: Rate limiting, input validation, CORS protection

---

## 🔒 Security Features

✅ **Rate Limiting**: Upload (8/hour), Query (30/min)  
✅ **Input Validation**: Query sanitization, file validation  
✅ **CORS Protection**: Specific domain allowlist  
✅ **File Security**: MIME type validation, size limits  
✅ **Code Injection Protection**: JSON parsing, pattern detection

---

## 🚀 Future Enhancements

### 🔄 CI/CD Pipeline
- **Automated Deployments**: Link GitHub repo directly with Vercel/Railway
- **Branch Previews**: Auto-deploy feature branches for testing
- **Automated Testing**: Run tests on every pull request
- **Environment Promotion**: Staging → Production workflow

### 🤖 RAG (Retrieval Augmented Generation)
- **Enhanced Query Understanding**: Use LLM to better interpret business questions
- **Contextual Responses**: Generate natural language explanations for results
- **Query Suggestions**: AI-powered query recommendations based on data
- **Benefits**: More intuitive interaction, better business insights, reduced learning curve

### 📊 Advanced Analytics
- **Query Analytics**: Track most common queries and user patterns
- **Performance Metrics**: Response times, accuracy scoring
- **Usage Dashboard**: Admin interface for monitoring application health
- **A/B Testing**: Compare different search algorithms

### 🔍 Enhanced Search Features
- **Multi-file Search**: Query across multiple uploaded spreadsheets
- **Advanced Filters**: Date ranges, numerical thresholds, category filters
- **Search History**: Save and replay previous queries
- **Export Results**: Download search results as CSV/PDF

### 🛡️ Enterprise Features
- **User Authentication**: Login/signup with role-based access
- **Team Workspaces**: Shared spreadsheets and collaborative querying
- **API Rate Limiting per User**: More granular usage controls
- **Audit Logs**: Track all data access and modifications

### 🎨 UX/UI Improvements
- **Dark Mode**: Theme switching for better user experience
- **Mobile Optimization**: Enhanced mobile interface
- **Keyboard Shortcuts**: Power user productivity features
- **Real-time Collaboration**: Multiple users querying simultaneously

### 🔧 Technical Enhancements
- **Caching Layer**: Redis for faster repeated queries
- **Database Migration**: Move to PostgreSQL for better scalability
- **Monitoring**: Add Prometheus/Grafana for detailed metrics
- **Load Testing**: Ensure performance under high traffic

### 🌐 Integration Capabilities
- **Google Sheets API**: Direct integration with Google Sheets
- **Excel Online**: Microsoft Excel integration
- **Slack/Teams Bots**: Query spreadsheets from chat platforms
- **Zapier Integration**: Connect with workflow automation tools

### 📱 Additional Formats
- **Excel Support**: .xlsx file processing
- **JSON/API Data**: Direct API data ingestion
- **Database Connections**: PostgreSQL, MySQL, MongoDB integrations
- **Real-time Data**: WebSocket connections for live data updates

---

## 🙌 Author

**Saket S Narayan**  
Frontend/Full-Stack Developer  
https://github.com/saket2508
