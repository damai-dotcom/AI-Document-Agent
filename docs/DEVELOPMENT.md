# Confluence Finder Development Guide

## 🎯 Project Overview

This is an AI-driven Confluence document search system developed in one week, aimed at solving the problem of difficult-to-find internal Confluence documents within enterprises.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Python Backend│    │  Confluence API │
│                 │    │                 │    │                 │
│ - User Interface│◄──►│ - Search API    │◄──►│ - Document Fetch│
│ - Result Display│    │ - AI Q&A        │    │ - Space Management│
│ - Admin Panel   │    │ - Vector Search │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ChromaDB      │
                       │                 │
                       │ - Vector Storage│
                       │ - Semantic Search│
                       │ - Document Index│
                       └─────────────────┘
```

## 🚀 Quick Start

### 1. Environment Setup

**Required Software:**

- Node.js 16+
- Python 3.8+
- OpenAI API Key
- Confluence access permissions

### 2. Configuration Steps

1. **Clone Project**

```bash
git clone <repository-url>
cd confluence_finder
```

2. **Install Dependencies**

```bash
npm run install:all
```

3. **Configure Environment Variables**

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
OPENAI_API_KEY=your_openai_api_key
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your_email@example.com
CONFLUENCE_API_TOKEN=your_api_token
```

4. **Start Application**

```bash
# Windows
start.bat

# Linux/Mac
./deploy.sh
npm run dev
```

## 🔧 Core Features

### 1. Smart Search

- Semantic-based document retrieval
- AI-driven answer generation
- Relevance score ranking

### 2. Document Indexing

- Automatic document sync from Confluence
- Intelligent text chunking
- Vectorized storage

### 3. User Interface

- Modern React interface
- Responsive design
- Real-time search feedback

## 📁 Project Structure

```
confluence_finder/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.tsx         # Main application
│   │   └── main.tsx        # Entry file
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # Python backend
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variable template
├── docs/                   # Documentation
├── start.bat              # Windows startup script
├── deploy.sh              # Linux deployment script
└── README.md
```

## 🛠️ Development Guide

### Frontend Development

```bash
cd frontend
npm run dev    # Development server
npm run build  # Production build
```

### Backend Development

```bash
cd backend
python app.py  # Start Flask server
```

### API Endpoints

**Search Documents**

```
POST /api/search
{
  "query": "How to apply for annual leave?"
}
```

**Index Documents**

```
POST /api/index
```

## 🔍 Technical Details

### Vector Search

- Use `SentenceTransformer` to generate document embeddings
- ChromaDB for storing and retrieving vectors
- Cosine similarity for relevance calculation

### AI Q&A

- OpenAI GPT-3.5-turbo model
- Generate answers based on retrieved documents
- Support contextual conversations

### Document Processing

- HTML content cleaning
- Intelligent text chunking
- Token limit management

## 📈 Performance Optimization

1. **Caching Strategy**

   - Document embedding cache
   - Search result cache

2. **Database Optimization**

   - Vector index optimization
   - Batch processing

3. **Frontend Optimization**
   - Component lazy loading
   - Search debouncing

## 🚨 Important Notes

1. **API Limitations**

   - OpenAI API call limits
   - Confluence API rate limits

2. **Security**

   - Secure storage of API keys
   - User permission verification

3. **Scalability**
   - Support for multiple data sources
   - Distributed deployment

## 🎨 UI/UX Design Principles

1. **Simplicity** - Clear visual hierarchy
2. **Responsiveness** - Adapt to various devices
3. **Accessibility** - Barrier-free design
4. **Feedback** - Real-time status indicators

## 🏆 Competitive Advantages

1. **Technical Innovation** - AI + Vector Search
2. **Practical Value** - Solves real pain points
3. **User Experience** - Simple and easy to use
4. **Scalability** - Supports enterprise deployment

## 📞 Technical Support

If you encounter issues, please check:

1. Environment variable configuration
2. API key validity
3. Network connection status
4. Dependency package versions

---

Good luck with the competition! 🎉
