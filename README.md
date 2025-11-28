# Confluence Finder - Local Document Search System

## Problem Statement

Organizations face challenges in efficiently searching and retrieving relevant information from large document repositories like Confluence. Traditional keyword-based search often fails to understand semantic context and meaning, leading to poor search results and reduced productivity. This project addresses the need for an intelligent document search system that can understand both Chinese and English queries, providing accurate and contextually relevant results through semantic search capabilities.

## Key Features Implemented

- ✅ **Bilingual Semantic Search**: Support for both Chinese and English queries using multilingual embedding model
- ✅ **Vector Database Integration**: ChromaDB for efficient document vector storage and retrieval
- ✅ **RAG Architecture**: Retrieval-Augmented Generation for intelligent document Q&A
- ✅ **Local Processing**: All document data stored locally, only external LLM calls for Q&A
- ✅ **Multiple LLM Support**: Configurable support for OpenAI, Claude, and Kimi LLM services
- ✅ **Web Interface**: Clean and responsive search interface
- ✅ **Batch Data Import**: Automated document processing and vectorization
- ✅ **Chunk-based Processing**: Intelligent text chunking to handle large documents
- ✅ **RESTful API**: Clean API endpoints for integration and testing

## Technical Design & Architecture

### System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │   External LLM  │
│                 │    │                  │    │                 │
│ - Web UI        │◄──►│ - Flask Server   │◄──►│ - OpenAI/Claude │
│ - Search Input  │    │ - Vector Search  │    │ - Kimi          │
│ - Results Display│   │ - LLM Integration│    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Local Storage   │
                    │                  │
                    │ - ChromaDB       │
                    │ - Document JSON  │
                    │ - Model Cache    │
                    └──────────────────┘
```

### Core Components

#### 1. Document Processing Pipeline
- **Data Importer**: Processes JSON documents and creates vector embeddings
- **Text Chunking**: Intelligent splitting of large documents using token-based chunking
- **Embedding Generation**: Uses `paraphrase-multilingual-MiniLM-L12-v2` for multilingual embeddings

#### 2. Vector Search Engine
- **ChromaDB Integration**: Persistent vector database for document storage
- **Similarity Search**: Cosine similarity-based document retrieval
- **Metadata Filtering**: Rich metadata support for refined search results

#### 3. LLM Integration Layer
- **Multi-LLM Support**: Configurable LLM backends (OpenAI, Claude, Kimi)
- **Context Enhancement**: Combines retrieved documents with user queries
- **Response Generation**: Intelligent answer generation based on retrieved context

#### 4. Web Service Layer
- **Flask Backend**: RESTful API with CORS support
- **Error Handling**: Comprehensive error handling and logging
- **Health Monitoring**: Health check and statistics endpoints

### Data Flow

1. **Document Ingestion**: JSON documents → Text chunking → Vector embeddings → ChromaDB storage
2. **Query Processing**: User query → Vector embedding → Similarity search → Document retrieval
3. **Answer Generation**: Retrieved documents + Query → LLM context → Generated response

### Technology Stack

- **Backend Framework**: Flask with CORS support
- **Vector Database**: ChromaDB (persistent storage)
- **Embedding Model**: Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **LLM Integration**: OpenAI API, Claude API, Kimi API
- **Frontend**: HTML5, CSS3, JavaScript with modern UI
- **Text Processing**: tiktoken for token-based chunking
- **Configuration**: Environment-based configuration management

## File Structure

```
confluence_finder/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── data_importer.py       # Document processing and vectorization
│   ├── config.py              # Configuration management
│   ├── kimi_llm.py           # Kimi LLM integration
│   ├── .env.example          # Environment variables template
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/                  # Frontend source code
│   ├── dist/                 # Built frontend assets
│   └── package.json          # Node.js dependencies
├── data/
│   └── confluence_export.json # Document data source
├── chroma_db/                # Vector database storage
├── model_cache/              # Model caching directory
├── docs/                     # Documentation
├── scripts/
│   ├── start_services.sh     # Service startup script
│   ├── import_data.sh        # Data import script
│   └── refresh_vector_db.bat  # Windows batch script
├── README.md                 # This documentation
├── requirements.txt          # Main Python dependencies
└── config.py                 # Global configuration
```

## Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd confluence_finder

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys and configuration
```

### 2. Data Import
```bash
# Import documents to vector database (Linux/Mac)
./import_data.sh

# Or on Windows
./refresh_vector_db.bat
```

### 3. Start Services
```bash
# Start all services
./start_services.sh

# Or start backend only
cd backend
python app.py
```

### 4. Access the Application
- **Web Interface**: http://localhost:5001
- **API Health Check**: http://localhost:5001/health
- **Statistics**: http://localhost:5001/stats

## API Documentation

### Search Documents
```http
POST /search
Content-Type: application/json

{
    "query": "employee onboarding process",
    "top_k": 5
}
```

**Response:**
```json
{
    "success": true,
    "query": "employee onboarding process",
    "documents": [
        {
            "title": "Employee Onboarding Guide",
            "content": "New employee orientation process...",
            "url": "https://confluence.company.com/onboarding",
            "similarity_score": 0.85,
            "metadata": {
                "space_key": "HR",
                "page_id": "12345",
                "chunk_index": 0
            }
        }
    ],
    "llm_response": "Based on the documents, the employee onboarding process involves...",
    "total": 3
}
```

### System Statistics
```http
GET /stats
```

**Response:**
```json
{
    "total_documents": 150,
    "collection_name": "confluence_docs",
    "model_info": {
        "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "llm_type": "openai"
    },
    "system_status": "healthy"
}
```

### Health Check
```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "timestamp": "2025-11-27T10:30:00Z",
    "services": {
        "chromadb": "connected",
        "embedding_model": "loaded",
        "llm_service": "available"
    }
}
```

## Configuration

### Environment Variables
```bash
# Database Configuration
CHROMA_DB_PATH=./chroma_db

# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
LLM_TYPE=openai  # openai, claude, kimi

# Confluence Configuration (if needed)
CONFLUENCE_URL=https://your-confluence.com
CONFLUENCE_USERNAME=your_username
CONFLUENCE_API_TOKEN=your_api_token
```

### Model Configuration
```python
# config.py
class Config:
    # Embedding model
    SENTENCE_TRANSFORMER_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
    
    # Search parameters
    DEFAULT_TOP_K = 5
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
```

## Development

### Adding New Documents
1. Update `data/confluence_export.json` with new document data
2. Run the import script to update the vector database
3. Documents will be automatically chunked and vectorized

### Extending LLM Support
1. Create new LLM service class in `backend/`
2. Add configuration options to `config.py`
3. Update `AIAnswerGenerator` class to support new LLM

### Customizing Search
- Modify `LocalVectorSearch.search_documents()` for custom search logic
- Adjust chunking parameters in `chunk_text()` method
- Update similarity thresholds in search results processing

## Performance Considerations

- **Model Caching**: Embedding models are cached to improve startup time
- **Batch Processing**: Documents are processed in batches for efficiency
- **Vector Indexing**: ChromaDB provides optimized vector indexing
- **Memory Management**: Large documents are chunked to handle memory constraints

## Troubleshooting

### Common Issues

1. **Model Loading Issues**
   - Ensure sufficient disk space for model caching
   - Check internet connection for initial model download

2. **Database Connection Errors**
   - Verify ChromaDB path permissions
   - Check available disk space for vector database

3. **LLM API Errors**
   - Validate API keys in environment configuration
   - Check API rate limits and quotas

### Logging
- Application logs are configured at INFO level
- Check console output for detailed error messages
- Vector database operations are logged for debugging

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For questions and support, please refer to the project documentation or create an issue in the repository.