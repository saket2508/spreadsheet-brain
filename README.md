# 🧠 Spreadsheet Brain – Semantic Search for Spreadsheets

This project is a prototype built as part of a hiring assignment for Superjoin. It allows users to upload a spreadsheet (CSV) and query it using natural language. The system performs semantic search to return the most relevant rows based on meaning, not just exact matches.

---

## 🚀 Features

- Upload `.csv` files with structured tabular data
- Each row is converted into a semantic text representation
- Embeddings are generated using OpenAI's `text-embedding-3-small` model via LangChain
- Row-level embeddings are stored in ChromaDB (local vector store)
- Users can later query the spreadsheet using natural language
- Semantic search returns top-K most relevant rows

---

## 🧱 Tech Stack

| Layer      | Tool       | Purpose                        |
| ---------- | ---------- | ------------------------------ |
| Backend    | FastAPI    | API server                     |
| AI Layer   | LangChain  | Embedding + semantic search    |
| Embeddings | OpenAI API | Text-to-vector conversion      |
| Vector DB  | ChromaDB   | Similarity search              |
| Data Utils | Pandas     | CSV reading and row formatting |

---

## 📁 Project Structure

```
spreadsheet-brain/
├── backend/
│   ├── main.py               # FastAPI app entrypoint
│   ├── utils.py              # CSV parsing and row -> text helpers
│   ├── vector_store.py       # LangChain + Chroma embedding logic
│   ├── models.py             # Pydantic models (if needed later)
│   └── requirements.txt      # Python dependencies
├── .env                      # OpenAI API key
└── README.md
```

---

## 🛠️ Setup Instructions

### 1. Clone the repo

```bash
git clone <repo-url>
cd spreadsheet-brain/backend
```

### 2. Create `.env` file

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

Access Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📦 API Endpoints

### POST `/upload`

- Accepts: `.csv` file via `multipart/form-data`
- Parses spreadsheet → generates row embeddings → stores in Chroma
- Returns: confirmation, row count, and sample data

---

## 🧠 How It Works (Architecture)

1. User uploads a CSV
2. Server reads it using `pandas`
3. Each row is converted into a natural language string
4. LangChain + OpenAI embed each row into a high-dimensional vector
5. Vectors are stored in ChromaDB for fast similarity search
6. Future `/query` route will accept a user question and return best matching rows

---

## ✅ What’s Done So Far

- [x] File upload route `/upload`
- [x] Parses CSV → row strings
- [x] Row embeddings with OpenAI
- [x] Embeddings stored in ChromaDB

---

## 🚧 Next Steps

- Implement `/query` route for semantic search
- Build React frontend to upload files and run queries
- Add metadata view and similarity scores

---

## 🧪 Example CSV Format

```csv
Name,Email,Location,Interest
Alice,alice@gmail.com,San Francisco,AI
Bob,bob@abc.com,New York,Product Design
```

---

## 📜 License

MIT

---

## 🙌 Author

**Saket S Narayan**  
Frontend/Full-Stack Developer  
https://github.com/saket2508

---

## 🐳 Docker Deployment

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### Setup Instructions

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

### Docker Architecture
- **Backend**: FastAPI container with ChromaDB persistence
- **Frontend**: Multi-stage build (Node.js → Nginx) with API proxy
- **Networking**: Internal Docker network for service communication
- **Volumes**: ChromaDB data persists across container restarts
