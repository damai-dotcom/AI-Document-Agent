#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration file for Confluence Finder
"""

import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Flask configuration
    HOST = '0.0.0.0'
    PORT = 5001
    DEBUG = False
    
    # ChromaDB configuration
    CHROMA_DB_PATH = './chroma_db'
    COLLECTION_NAME = 'confluence_docs'
    
    # Model configuration
    SENTENCE_TRANSFORMER_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
    MODEL_CACHE_PATH = r'e:\development\confluence_finder\model_cache'
    
    # AWS Bedrock configuration
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    # Note: AWS credentials will be automatically loaded from IAM role (EC2) or environment variables
    
    # Bedrock model configuration
    BEDROCK_MODEL_TYPE = os.getenv('BEDROCK_MODEL_TYPE', 'claude')  # claude, titan, llama
    CLAUDE_MODEL_ID = 'anthropic.claude-3-sonnet-20240229-v1:0'
    TITAN_MODEL_ID = 'amazon.titan-text-express-v1'
    LLAMA_MODEL_ID = 'meta.llama3-8b-instruct-v1:0'
    
    # LLM parameters
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # Search configuration
    DEFAULT_TOP_K = 5
    
    @classmethod
    def get_bedrock_config(cls) -> dict:
        """Get Bedrock configuration"""
        return {
            'region_name': cls.AWS_REGION
        }
    
    @classmethod
    def get_model_id(cls, model_type: str) -> str:
        """Get model ID by type"""
        model_map = {
            'claude': cls.CLAUDE_MODEL_ID,
            'titan': cls.TITAN_MODEL_ID,
            'llama': cls.LLAMA_MODEL_ID
        }
        return model_map.get(model_type.lower(), cls.CLAUDE_MODEL_ID)