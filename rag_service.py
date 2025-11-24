#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simplified RAG Service - Bilingual Semantic Search (Chinese-English)
Using paraphrase-multilingual-MiniLM-L12-v2 model
"""

import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
# 设置模型下载路径到E盘
os.environ['TRANSFORMERS_CACHE'] = r'e:\development\confluence_finder\model_cache'
os.environ['HF_HOME'] = r'e:\development\confluence_finder\model_cache'
os.environ['HUGGINGFACE_HUB_CACHE'] = r'e:\development\confluence_finder\model_cache'

import json
import chromadb
import numpy as np
from typing import List, Dict
from datetime import datetime
from sentence_transformers import SentenceTransformer
from bedrock_llm import BedrockLLMService
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SimpleRAGService:
    """Simplified RAG Service - Bilingual Semantic Search"""
    
    def __init__(self):
        """Initialize service"""
        try:
            # 初始化ChromaDB
            self.chroma_client = chromadb.PersistentClient(path='./chroma_db')
            self.collection = self.chroma_client.get_collection(name="confluence_docs")
            
            # 初始化多语言模型
            self.model = SentenceTransformer(
                "paraphrase-multilingual-MiniLM-L12-v2", 
                cache_folder=r"e:\development\confluence_finder\model_cache",
                use_auth_token=False,
                local_files_only=True
            )
            
            # Initialize Bedrock LLM service
            try:
                self.bedrock_llm = BedrockLLMService(region_name=Config.AWS_REGION)
                self.use_bedrock = True
                logger.info("Bedrock LLM service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Bedrock LLM: {e}. Using mock responses.")
                self.bedrock_llm = None
                self.use_bedrock = False
            
            # Check data
            count = self.collection.count()
            if count == 0:
                raise Exception("No data found in ChromaDB")
            
            logger.info(f"RAG service initialized successfully with {count} documents")
            logger.info("Using paraphrase-multilingual-MiniLM-L12-v2 model for semantic search")
            if self.use_bedrock:
                logger.info(f"Using Bedrock LLM with model: {Config.BEDROCK_MODEL_TYPE}")
            else:
                logger.info("Using mock LLM responses")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    def search_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Document search - Bilingual support (Chinese-English)"""
        if not query or len(query.strip()) < 1:
            return []
        
        logger.info(f"Search query: '{query}'")
        
        try:
            # Use MiniLM model for semantic search
            query_embedding = self.model.encode([query])
            
            # ChromaDB semantic search
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k
            )
            
            # Process results
            documents = []
            
            for i, (doc_id, distance, doc, metadata) in enumerate(zip(
                results['ids'][0], 
                results['distances'][0], 
                results['documents'][0], 
                results['metadatas'][0]
            )):
                # Convert distance to similarity
                # ChromaDB uses cosine distance, use improved conversion for high distances
                if distance < 1.0:
                    # Normal cosine similarity conversion
                    similarity = 1 - distance
                else:
                    # Exponential decay conversion for abnormal high distances
                    similarity = np.exp(-distance / 10)
                
                # Ensure similarity is within [0,1] range
                similarity = max(0.0, min(1.0, similarity))
                
                # Keep all results
                documents.append({
                        'id': doc_id,
                        'title': metadata.get('title', ''),
                        'content': doc,
                        'url': metadata.get('url', ''),
                        'category': metadata.get('space_name', ''),
                        'similarity': similarity
                    })
            
            logger.info(f"Found {len(documents)} related documents")
            
            # Sort by similarity
            documents.sort(key=lambda x: x['similarity'], reverse=True)
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def generate_llm_response(self, query: str, documents: List[Dict]) -> str:
        """Generate LLM response using Bedrock or mock"""
        if not documents:
            return "Sorry, no relevant information found. Please try more specific keywords."
        
        # Use Bedrock if available
        if self.use_bedrock and self.bedrock_llm:
            try:
                return self.bedrock_llm.generate_rag_response(
                    query=query,
                    documents=documents,
                    model_type=Config.BEDROCK_MODEL_TYPE
                )
            except Exception as e:
                logger.error(f"Bedrock LLM call failed: {e}. Falling back to mock response.")
                return self._mock_llm_response(query, documents)
        else:
            # Use mock response
            return self._mock_llm_response(query, documents)
    
    def _mock_llm_response(self, query: str, documents: List[Dict]) -> str:
        """Mock LLM response (fallback)"""
        if len(documents) == 1:
            doc = documents[0]
            return f"""Based on your question, I found the following relevant information:

**Document Title:** {doc['title']}
**Similarity:** {doc['similarity']:.1%}
**Category:** {doc['category']}

**Content Summary:**
{doc['content'][:200]}...

Please review the full document content or ask more specific questions."""
        
        categories = list(set(doc['category'] for doc in documents if doc['category']))
        main_category = categories[0] if categories else "Unknown"
        
        return f"""Based on your question, I found {len(documents)} related documents.

**Main Category:** {main_category}

**Related Documents:**
{chr(10).join([f"• {doc['title']} (Similarity: {doc['similarity']:.1%})" for doc in documents])}

Please review the above documents for details or ask more specific questions for more precise answers."""

# Initialize service
try:
    rag_service = SimpleRAGService()
    logger.info("RAG service started successfully")
except Exception as e:
    logger.error(f"RAG service startup failed: {e}")
    rag_service = None

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint"""
    try:
        if not rag_service:
            return jsonify({'success': False, 'error': 'RAG service not initialized'})
        
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'success': False, 'error': 'Query cannot be empty'})
        
        # Retrieve documents
        documents = rag_service.search_documents(query, top_k=5)
        
        # Generate LLM response (Bedrock or mock)
        llm_response = rag_service.generate_llm_response(query, documents)
        
        return jsonify({
            'success': True,
            'query': query,
            'documents': documents,
            'llm_response': llm_response,
            'total': len(documents)
        })
        
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stats', methods=['GET'])
def stats():
    """Statistics endpoint"""
    try:
        if not rag_service:
            return jsonify({'success': False, 'error': 'RAG service not initialized'})
        
        count = rag_service.collection.count()
        return jsonify({
            'success': True,
            'total_documents': count,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Statistics endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy' if rag_service else 'unhealthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/')
def index():
    """Simple test page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confluence Finder - Semantic Search</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .search-box { margin-bottom: 20px; }
        input[type="text"] { width: 70%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { padding: 12px 20px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-left: 10px; }
        button:hover { background-color: #0056b3; }
        .doc-item { border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; background-color: #f9f9f9; }
        .doc-title { font-weight: bold; color: #333; margin-bottom: 5px; }
        .doc-meta { color: #666; font-size: 14px; margin-bottom: 10px; }
        .doc-content { color: #444; line-height: 1.5; }
        .llm-response { background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #007bff; }
        .error { color: #dc3545; background-color: #f8d7da; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Confluence Finder - Semantic Search</h1>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Enter search keywords (supports Chinese and English)..." />
            <button onclick="search()">Search</button>
        </div>
        
        <div id="results"></div>
    </div>

    <script>
        async function search() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                alert('Please enter search keywords');
                return;
            }
            
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div>🔍 Searching...</div>';
            
            try {
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: query })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    displayResults(data);
                } else {
                    resultsDiv.innerHTML = `<div class="error">Search failed: ${data.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="error">Network error: ${error.message}</div>`;
            }
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            let html = '';
            
            if (data.total === 0) {
                html = '<div class="error">No relevant documents found. Please try other keywords.</div>';
            } else {
                html = `<h3>📄 Found ${data.total} relevant documents</h3>`;
                
                data.documents.forEach((doc, index) => {
                    html += `
                        <div class="doc-item">
                            <div class="doc-title">${index + 1}. ${doc.title}</div>
                            <div class="doc-meta">
                                📁 ${doc.category} | 
                                🔗 <a href="${doc.url}" target="_blank">View Original</a> | 
                                📊 Similarity: ${(doc.similarity * 100).toFixed(1)}%
                            </div>
                            <div class="doc-content">${doc.content.substring(0, 200)}...</div>
                        </div>
                    `;
                });
                
                if (data.llm_response) {
                    html += `
                        <div class="llm-response">
                            <strong>🤖 AI Response:</strong><br>
                            ${data.llm_response.replace(/\\n/g, '<br>')}
                        </div>
                    `;
                }
            }
            
            resultsDiv.innerHTML = html;
        }
        
        // Support Enter key for search
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                search();
            }
        });
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    logger.info("Starting RAG service...")
    app.run(host='0.0.0.0', port=5001, debug=False)