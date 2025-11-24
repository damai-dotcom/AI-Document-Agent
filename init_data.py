#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize English Data for Confluence Finder
"""

import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_data():
    """Initialize English data into ChromaDB"""
    try:
        # Initialize ChromaDB
        chroma_client = chromadb.PersistentClient(path='./chroma_db')
        collection = chroma_client.get_or_create_collection(name="confluence_docs")
        
        # Clear existing data
        try:
            # Get all existing IDs and delete them
            existing_data = collection.get()
            if existing_data['ids']:
                collection.delete(ids=existing_data['ids'])
        except Exception as e:
            logger.warning(f"Could not clear existing data: {e}")
        
        # Load data
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'confluence_export.json')
        
        if not os.path.exists(data_file):
            logger.error(f"Data file not found: {data_file}")
            return False
        
        with open(data_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        for doc in export_data.get('docs', []):
            documents.append(doc['content'])
            metadatas.append({
                'title': doc.get('title', ''),
                'url': doc.get('url', ''),
                'space_key': doc.get('space_key', ''),
                'space_name': doc.get('space_name', ''),
                'id': doc.get('id', ''),
                'author': doc.get('author', ''),
                'created_date': doc.get('created_date', ''),
                'updated_date': doc.get('updated_date', '')
            })
            ids.append(doc.get('id', f"doc_{len(ids)}"))
        
        # Initialize sentence transformer model
        logger.info("Loading sentence transformer model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Generate embeddings
        logger.info("Generating document embeddings...")
        embeddings = model.encode(documents)
        
        # Add to ChromaDB
        logger.info("Adding documents to ChromaDB...")
        collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully initialized {len(documents)} documents")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize data: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting data initialization...")
    success = initialize_data()
    
    if success:
        logger.info("Data initialization completed successfully!")
    else:
        logger.error("Data initialization failed!")