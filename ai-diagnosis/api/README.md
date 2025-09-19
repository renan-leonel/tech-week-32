# 🤖 AI Diagnosis System

An intelligent diagnosis system that combines **document analysis** with **sensor data monitoring** to provide AI-powered insights for industrial equipment monitoring and maintenance.

## 🚀 Features

### 📄 Document Analysis (RAG)
- **PDF Processing**: Upload and analyze technical documents, manuals, and reports
- **Smart Embeddings**: Generate vector embeddings using OpenAI's latest models
- **Intelligent Q&A**: Ask questions about uploaded documents using advanced LLMs
- **Multi-Provider Support**: OpenAI GPT-4 and Google Gemini models

### 📊 Sensor Data Management
- **Real-time Monitoring**: Track sensor data from industrial equipment
- **Alert System**: Intelligent alerts based on configurable thresholds
- **Historical Analysis**: Query historical sensor data with advanced filtering
- **Statistics Dashboard**: Get insights into sensor performance and trends

### 🔧 Technical Features
- **FastAPI**: High-performance async API framework
- **PostgreSQL**: Robust database for sensor data storage
- **SQLAlchemy**: Modern ORM with full type support
- **Vector Storage**: FAISS-powered document embeddings
- **Auto Documentation**: Interactive API docs with Swagger UI

## 📦 Installation

### Prerequisites
- Python 3.12+
- PostgreSQL 14+
- OpenAI API Key (required)
- Google API Key (optional, for Gemini models)

### Quick Start

1. **Clone and Navigate**
   ```bash
   cd ai-diagnosis/api
   ```

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Set Environment Variables**
   Create a `.env` file or export variables:
   ```bash
   export DATABASE_URL="postgresql://sensor_user:sensor_password@localhost:5432/sensor_db"
   export OPENAI_API_KEY="your-openai-api-key"
   export GOOGLE_API_KEY="your-google-api-key"  # Optional
   ```

4. **Start the Server**
   ```bash
   uv run python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the API**
   - **Interactive Docs**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

## 🗄️ Database Setup

### PostgreSQL Installation (macOS)
```bash
# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Create database and user
createdb sensor_db
psql sensor_db -c "CREATE USER sensor_user WITH PASSWORD 'sensor_password';"
psql sensor_db -c "GRANT ALL PRIVILEGES ON DATABASE sensor_db TO sensor_user;"
```

### Create Tables
```bash
export DATABASE_URL="postgresql://sensor_user:sensor_password@localhost:5432/sensor_db"
uv run python services/database/create_table.py
```

## 🛠️ API Endpoints

### 📄 LLM & Document Processing (`/llm`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/llm/models` | List available LLM models |
| `POST` | `/llm/documents` | Upload PDFs and generate embeddings |
| `POST` | `/llm/question` | Ask questions about documents using RAG |

### 📊 Sensor Data & Database (`/sensors`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/sensors/data` | Get sensor data with filtering and pagination |
| `GET` | `/sensors/data/count` | Count total sensor records |
| `GET` | `/sensors/alerts` | Get alerts based on threshold violations |
| `GET` | `/sensors/{sensor_id}/data` | Get data for specific sensor |
| `GET` | `/sensors/recent` | Get recent sensor data (last N hours) |
| `GET` | `/sensors/stats` | Get database statistics |

## 💡 Usage Examples

### Document Analysis
```bash
# Upload a PDF document
curl -X POST "http://localhost:8000/llm/documents" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@manual.pdf"

# Ask a question about the document
curl -X POST "http://localhost:8000/llm/question" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the maintenance requirements?",
    "llm_provider": "openai",
    "model": "gpt-4o",
    "document_ids": ["manual"]
  }'
```

### Sensor Data Queries
```bash
# Get recent sensor data
curl "http://localhost:8000/sensors/recent?hours=24&limit=50"

# Get alerts for critical issues
curl "http://localhost:8000/sensors/alerts?severity=critical"

# Get data for specific sensor
curl "http://localhost:8000/sensors/SENSOR001/data?limit=100"
```

## 📊 Sensor Data Model

The system tracks comprehensive sensor data including:

### 🌡️ Temperature Monitoring
- **Asset Temperature** > 120°C → Critical Alert
- **Environment Temperature** > 90°C → Warning Alert

### ⚡ Acceleration/Vibration
- **G-force measurements** (X, Y, Z axes)
- **Peak values** > 16G → Critical Alert
- **RMS values** and **Crest factors**

### 📡 Connectivity
- **Gateway Signal** < -85 dBm → Warning Alert
- **Power status** monitoring

## 🚨 Alert System

The system provides intelligent alerts based on configurable thresholds:

| Alert Type | Threshold | Severity | Description |
|------------|-----------|----------|-------------|
| High Asset Temperature | > 120°C | Critical | Equipment overheating |
| High Environment Temperature | > 90°C | Warning | Ambient temperature too high |
| High G-force | > 16G | Critical | Excessive vibration detected |
| Weak Signal | < -85 dBm | Warning | Poor connectivity |

## 🧪 Development

### Project Structure
```
api/
├── main.py                     # FastAPI application
├── routes/
│   ├── llm.py                 # LLM and document routes
│   ├── database.py            # Sensor data routes
│   └── main.py                # Legacy routes (deprecated)
├── services/
│   ├── embeddings.py          # Document processing
│   ├── llm.py                 # Language model services
│   └── database/
│       ├── models.py          # SQLAlchemy models
│       ├── database.py        # Database connection
│       └── create_table.py    # Database setup
└── vector_store/              # Document embeddings storage
```

### Dependencies
- **FastAPI** - Modern web framework
- **SQLAlchemy** - Database ORM
- **psycopg2-binary** - PostgreSQL adapter
- **langchain** - LLM framework
- **openai** - OpenAI API client
- **faiss-cpu** - Vector similarity search
- **pypdf** - PDF processing

### Environment Configuration
```bash
# Required
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
OPENAI_API_KEY=your-openai-api-key

# Optional
GOOGLE_API_KEY=your-google-api-key
```

## 🔐 Security Notes

- Store API keys securely (use `.env` file, never commit to git)
- Configure database with appropriate user permissions
- Use HTTPS in production
- Implement rate limiting for production use

## 📈 Performance

- **Async operations** for high concurrency
- **Database indexing** on frequently queried columns
- **Vector embeddings** cached locally
- **Pagination** for large datasets

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check if PostgreSQL is running
   brew services list | grep postgresql
   
   # Restart if needed
   brew services restart postgresql@14
   ```

2. **Missing Dependencies**
   ```bash
   uv sync  # Reinstall all dependencies
   ```

3. **API Key Issues**
   ```bash
   # Verify environment variables
   echo $OPENAI_API_KEY
   ```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support or questions:
- Check the API documentation at `/docs`
- Review the troubleshooting section above
- Open an issue in the repository

---

**Built with ❤️ using FastAPI, PostgreSQL, and OpenAI**
