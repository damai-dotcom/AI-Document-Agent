"""
Confluence Document Data Import Tool
For importing Confluence documents into local vector database
"""
import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import tiktoken
import logging
from datetime import datetime
# Import configuration
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceDataImporter:
    def __init__(self):
        self.base_url = os.getenv('CONFLUENCE_URL')
        self.username = os.getenv('CONFLUENCE_USERNAME')
        self.api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.auth = (self.username, self.api_token)
        
        # Local storage path
        self.data_dir = '../data'
        self.export_file = os.path.join(self.data_dir, 'confluence_export.json')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(Config.SENTENCE_TRANSFORMER_MODEL)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_DB_PATH', './chroma_db'))
        self.collection = self.chroma_client.get_or_create_collection(name="confluence_docs")
    
    def get_spaces(self):
        """Get all spaces"""
        try:
            url = f"{self.base_url}/wiki/rest/api/space"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get spaces: {str(e)}")
            return None
    
    def get_pages_in_space(self, space_key, limit=100):
        """Get all pages in space"""
        try:
            url = f"{self.base_url}/wiki/rest/api/content"
            params = {
                'spaceKey': space_key,
                'limit': limit,
                'expand': 'body.view,version'
            }
            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get pages: {str(e)}")
            return None
    
    def get_page_content(self, page_id):
        """Get page content"""
        try:
            url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
            params = {'expand': 'body.view,version'}
            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get page content: {str(e)}")
            return None
    
    def clean_html_content(self, html_content):
        """Clean HTML content and extract plain text"""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(strip=True)
    
    def chunk_text(self, text, max_tokens=800):
        """Chunk text to avoid exceeding token limits"""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = encoding.encode(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for token in tokens:
            if current_length + 1 > max_tokens:
                chunks.append(encoding.decode(current_chunk))
                current_chunk = [token]
                current_length = 1
            else:
                current_chunk.append(token)
                current_length += 1
        
        if current_chunk:
            chunks.append(encoding.decode(current_chunk))
        
        return chunks
    
    def export_all_docs(self):
        """Export all Confluence documents to local JSON file"""
        logger.info("Starting to export Confluence documents...")
        
        all_docs = []
        spaces = self.get_spaces()
        
        if not spaces:
            logger.error("Failed to get space information")
            return False
        
        for space in spaces.get('results', []):
            space_key = space.get('key')
            space_name = space.get('name', space_key)
            logger.info(f"Processing space: {space_name} ({space_key})")
            
            pages = self.get_pages_in_space(space_key)
            if not pages:
                continue
            
            for page in pages.get('results', []):
                page_id = page.get('id')
                page_title = page.get('title', '')
                
                logger.info(f"Exporting page: {page_title}")
                
                page_data = self.get_page_content(page_id)
                if not page_data:
                    continue
                
                content = self.clean_html_content(
                    page_data.get('body', {}).get('view', {}).get('value', '')
                )
                url = f"{self.base_url}/wiki/pages/viewpage.action?pageId={page_id}"
                
                # Save complete document information
                doc_info = {
                    'id': page_id,
                    'title': page_title,
                    'content': content,
                    'url': url,
                    'space_key': space_key,
                    'space_name': space_name,
                    'exported_at': datetime.now().isoformat()
                }
                
                all_docs.append(doc_info)
        
        # Save to local file
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_docs': len(all_docs),
            'docs': all_docs
        }
        
        with open(self.export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully exported {len(all_docs)} documents to {self.export_file}")
        return True
    
    def import_to_vector_db(self):
        """Import from local JSON file to vector database"""
        if not os.path.exists(self.export_file):
            logger.error(f"Export file does not exist: {self.export_file}")
            return False
        
        logger.info("Starting to import documents to vector database...")
        
        with open(self.export_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for doc in export_data['docs']:
            title = doc['title']
            content = doc['content']
            url = doc['url']
            space_key = doc['space_key']
            page_id = doc['id']
            
            # Chunk processing
            chunks = self.chunk_text(content)
            for i, chunk in enumerate(chunks):
                documents.append(f"{title}\n\n{chunk}")
                metadatas.append({
                    'title': title,
                    'url': url,
                    'space_key': space_key,
                    'page_id': page_id,
                    'chunk_index': i
                })
                ids.append(f"{page_id}_{i}")
        
        # Generate embeddings
        logger.info("Generating document embeddings...")
        embeddings = self.embedding_model.encode(documents)
        
        # Clear existing collection
        try:
            self.collection.delete()
            self.collection = self.chroma_client.get_or_create_collection(name="confluence_docs")
        except:
            pass
        
        # Add to ChromaDB
        logger.info("Saving to vector database...")
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully imported {len(documents)} document chunks to vector database")
        return True
    
    def full_import(self):
        """Complete import process: export documents + import to vector database"""
        logger.info("Starting complete import process...")
        
        # 1. Export documents to local
        if not self.export_all_docs():
            logger.error("Document export failed")
            return False
        
        # 2. Import to vector database
        if not self.import_to_vector_db():
            logger.error("Vector database import failed")
            return False
        
        logger.info("Complete import process finished!")
        return True

def main():
    """Main function"""
    # Check if command line argument is provided
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        # Interactive mode if no command line argument
        importer = ConfluenceDataImporter()
        
        print("Confluence Document Import Tool")
        print("1. Export documents to local")
        print("2. Import from local to vector database")
        print("3. Complete import")
        
        choice = input("Please select an operation (1/2/3): ").strip()
        
        if choice == '1':
            importer.export_all_docs()
        elif choice == '2':
            importer.import_to_vector_db()
        elif choice == '3':
            importer.full_import()
        else:
            print("Invalid choice")
        return
    
    # Command line mode
    importer = ConfluenceDataImporter()
    
    if mode == 'export':
        importer.export_all_docs()
    elif mode == 'import':
        importer.import_to_vector_db()
    elif mode == 'full':
        importer.full_import()
    else:
        print("Usage: python data_importer.py [export|import|full]")

if __name__ == "__main__":
    main()