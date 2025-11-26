"""
Confluence Finder - Local Version
All document data is stored locally, only external LLM is called for Q&A
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
import openai
import json
import logging
from sentence_transformers import SentenceTransformer
import requests
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kimi_llm import KimiLLMService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configure OpenAI (for Q&A only)
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure local ChromaDB
chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_DB_PATH', './chroma_db'))
collection = chroma_client.get_or_create_collection(name="confluence_docs")

# Import configuration
from config import Config

# Initialize local embedding model
embedding_model = SentenceTransformer(Config.SENTENCE_TRANSFORMER_MODEL)

# Local data file path
DATA_DIR = './data'
EXPORT_FILE = os.path.join(DATA_DIR, 'confluence_export.json')

class LocalVectorSearch:
    """Local Vector Search Engine"""
    
    def __init__(self):
        self.collection = collection
        self.embedding_model = embedding_model
    
    def search_documents(self, query, n_results=5):
        """Search for relevant documents"""
        try:
            # Generate query embedding
            logger.info(f"Generating embedding for query: {query}")
            query_embedding = self.embedding_model.encode([query])
            logger.info(f"Query embedding shape: {query_embedding.shape}")
            
            # Search for similar documents
            logger.info(f"Searching for {n_results} most similar documents...")
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            # Log search result details
            if results and 'documents' in results and results['documents']:
                logger.info(f"Found {len(results['documents'][0])} documents")
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results.get('metadatas', [[]])[0], 
                    results.get('distances', [[]])[0]
                )):
                    similarity_score = 1 / (1 + distance)
                    logger.info(f"Document {i+1}: Similarity={similarity_score:.4f}, Distance={distance:.4f}")
                    logger.info(f"  Title: {metadata.get('title', 'Unknown')}")
                    # Extract content after title for better preview
                    preview_parts = doc.split('\n\n', 1)
                    preview = preview_parts[1][:100] if len(preview_parts) > 1 else doc[:100]
                    logger.info(f"  Content preview: {preview}...")
            else:
                logger.warning("No documents found in search results")
            
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return None
    
    def get_collection_stats(self):
        """Get collection statistics"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {str(e)}")
            return None

class AIAnswerGenerator:
    """AI Answer Generator - Only calls external LLM"""
    
    def __init__(self):
        """
        Initialize the LLM service with configuration from environment variables.
        
        Loads API key, model type and specific model configurations from environment variables.
        Supports multiple LLM types including OpenAI, Claude and Kimi.
        
        Environment Variables:
            OPENAI_API_KEY: API key for OpenAI services
            OPENAI_MODEL: Model name for OpenAI (default: gpt-3.5-turbo)
            LLM_TYPE: Type of LLM service to use (openai, claude, kimi)
            
        Initializes specific service instances based on LLM_TYPE.
        """
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # Support multiple LLM interfaces
        self.llm_type = os.getenv('LLM_TYPE', 'openai')  # openai, claude, kimi
        
        # Initialize Kimi service
        if self.llm_type == 'kimi':
            self.kimi_service = KimiLLMService()
        
    def generate_answer(self, query, context_docs):
        """Generate answer using external LLM"""
        try:
            context = "\n\n".join([f"Document snippet {i+1}: {doc}" for i, doc in enumerate(context_docs)])
            
            if self.llm_type == 'openai':
                return self._generate_with_openai(query, context)
            elif self.llm_type == 'claude':
                return self._generate_with_claude(query, context)
            elif self.llm_type == 'kimi':
                return self._generate_with_kimi(query, context)
            else:
                return self._generate_with_openai(query, context)
                
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return None
    
    def _generate_with_openai(self, query, context):
        """Generate answer using OpenAI"""
        prompt = f"""You are a professional document assistant. Please answer the user's question based on the following Confluence document content.

Document content:
{context}

User question: {query}

Answer requirements:
1. Answer based on the provided document content
2. If there's no relevant information in the documents, please state so honestly
3. Answers should be accurate, concise, and helpful
4. You may appropriately reference document content

Answer:"""
        
        # 记录发送给OpenAI的请求
        logger.info(f"Sending request to OpenAI model: {self.model}")
        logger.info(f"Query: {query}")
        logger.info(f"Context length: {len(context)} characters")
        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.info(f"Context preview: {context[:200]}...")
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional enterprise document assistant, specialized in answering user questions based on provided document content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        # 记录OpenAI的响应
        logger.info(f"OpenAI response received")
        logger.info(f"Response length: {len(answer)} characters")
        logger.info(f"Response preview: {answer[:200]}...")
        logger.info(f"Tokens used: {response.usage.get('total_tokens', 'Unknown')}")
        
        return answer
    
    def _generate_with_claude(self, query, context):
        """Generate answer using Claude (reserved interface)"""
        # Claude API integration can be added here
        return self._generate_with_openai(query, context)
    
    def _generate_with_kimi(self, query, context):
        """Generate answer using Kimi"""
        try:
            # Prepare document data using regex to properly parse documents
            import re
            documents = []
            # Use regex to find all documents with their correct numbers and content
            document_pattern = r'Document snippet (\d+):([\s\S]+?)(?=Document snippet \d+:|$)'
            matches = re.finditer(document_pattern, context)
            
            for match in matches:
                snippet_num = match.group(1)
                content = match.group(2).strip()
                documents.append({
                    'title': f'Document snippet {snippet_num}',
                    'content': content,
                    'category': 'Knowledge Base',
                    'similarity': 0.8
                })
            
            # Log request sent to Kimi
            logger.info(f"Sending request to Kimi")
            logger.info(f"Query: {query}")
            logger.info(f"Number of documents: {len(documents)}")
            logger.info(f"Context length: {len(context)} characters")
            
            # Use Kimi service to generate RAG response
            response = self.kimi_service.generate_rag_response(query, documents)
            
            # Log Kimi response
            logger.info(f"Kimi response received")
            logger.info(f"Response length: {len(response)} characters")
            logger.info(f"Response preview: {response[:200]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating answer with Kimi: {str(e)}")
            # If Kimi fails, fall back to OpenAI
            logger.info("Falling back to OpenAI due to Kimi error")
            return self._generate_with_openai(query, context)

class DataManager:
    """Local Data Manager"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.export_file = EXPORT_FILE
    
    def get_export_info(self):
        """Get export information"""
        if not os.path.exists(self.export_file):
            return None
        
        try:
            with open(self.export_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'export_time': data.get('export_time'),
                'total_docs': data.get('total_docs', 0),
                'file_size': os.path.getsize(self.export_file)
            }
        except Exception as e:
            logger.error(f"Failed to read export information: {str(e)}")
            return None
    
    def check_data_exists(self):
        """Check if local data exists"""
        return os.path.exists(self.export_file)

# Initialize components
vector_search = LocalVectorSearch()
ai_generator = AIAnswerGenerator()
data_manager = DataManager()

@app.route('/api/search', methods=['POST'])
def search():
    """Search API - Fully local search + external LLM Q&A"""
    try:
        # Log detailed request information for debugging
        request_data = request.data.decode('utf-8')
        logger.info(f"Received search request: {request_data}")
        
        data = request.json
        if data is None:
            logger.error("Request body is not valid JSON")
            return jsonify({'error': 'Invalid JSON format'}), 400
            
        query = data.get('query', '')
        logger.info(f"Search query: {query}")
        
        if not query:
            logger.error("Query parameter is empty")
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Directly check if vector database has data
        collection_stats = vector_search.get_collection_stats()
        if collection_stats and collection_stats['total_documents'] > 0:
            logger.info(f"Vector database has {collection_stats['total_documents']} documents")
            data_exists = True
        else:
            logger.info("Vector database is empty")
            data_exists = False
        
        if not data_exists:
            logger.error("No data found in vector database")
            return jsonify({'error': 'Vector database is empty, please import documents first'}), 400
        
        # Local vector search
        search_results = vector_search.search_documents(query)
        
        if not search_results:
            return jsonify({'error': 'Search failed'}), 500
        
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0]
        
        # Log document information to be sent to LLM
        logger.info(f"Preparing to send {len(documents[:3])} documents to LLM")
        for i, doc in enumerate(documents[:3]):
            # Extract content after title for better preview
            preview_parts = doc.split('\n\n', 1)
            preview = preview_parts[1][:100] if len(preview_parts) > 1 else doc[:100]
            logger.info(f"Document {i+1} for LLM: {preview}...")
        
        # Generate answer using external LLM
        answer = ai_generator.generate_answer(query, documents[:3])
        
        # Log answer returned by LLM
        if answer:
            logger.info(f"LLM answer received: {answer[:100]}...")
        else:
            logger.warning("LLM returned empty answer")
        
        # Build results
        results = []
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # Calculate relevance score (0-1)
            score = 1 / (1 + distance)
            
            # Extract actual content without title for better display
            content_parts = doc.split('\n\n', 1)
            actual_content = content_parts[1] if len(content_parts) > 1 else ''
            
            result = {
                'title': metadata['title'],
                'content': actual_content,  # Store actual content without title
                'full_document': doc,      # Keep full document for reference
                'url': metadata['url'],
                'score': score,
                'space_key': metadata.get('space_key', ''),
                'chunk_index': metadata.get('chunk_index', 0)
            }
            
            # Only add AI answer to the first result
            if i == 0 and answer:
                result['answer'] = answer
            
            results.append(result)
        
        # Log final results returned to frontend
        logger.info(f"Returning {len(results)} results to frontend")
        logger.info(f"First result title: {results[0]['title']}")
        logger.info(f"First result score: {results[0]['score']}")
        
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"Search API error: {str(e)}")
        return jsonify({'error': 'Search failed, please try again later'}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """System Status API"""
    try:
        # Check data status
        export_info = data_manager.get_export_info()
        collection_stats = vector_search.get_collection_stats()
        
        return jsonify({
            'status': 'healthy',
            'data_exported': export_info is not None,
            'export_info': export_info,
            'collection_stats': collection_stats,
            'llm_type': ai_generator.llm_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({'error': 'Status check failed'}), 500

@app.route('/api/import/status', methods=['GET'])
def import_status():
    """Import Status API"""
    try:
        if data_manager.check_data_exists():
            export_info = data_manager.get_export_info()
            collection_stats = vector_search.get_collection_stats()
            
            return jsonify({
                'data_exists': True,
                'export_info': export_info,
                'collection_stats': collection_stats,
                'message': 'Local data is ready'
            })
        else:
            return jsonify({
                'data_exists': False,
                'message': 'Local data does not exist, please run the data import tool'
            })
            
    except Exception as e:
        logger.error(f"Error checking import status: {str(e)}")
        return jsonify({'error': 'Check failed'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Simple Health Check"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info("Starting Confluence Finder server...")
    logger.info(f"Local data directory: {DATA_DIR}")
    logger.info(f"Vector database path: {os.getenv('CHROMA_DB_PATH', './chroma_db')}")
    logger.info(f"LLM type: {ai_generator.llm_type}")
    
    app.run(host='0.0.0.0', port=port, debug=True)