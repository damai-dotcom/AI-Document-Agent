#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Bedrock LLM Service
Supports various models like Claude, Titan, Llama etc.
"""

import json
import logging
import boto3
from typing import Dict, List, Optional, Union
from botocore.exceptions import ClientError, NoCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BedrockLLMService:
    """Amazon Bedrock LLM Service"""
    
    def __init__(self, region_name: str = 'us-east-1'):
        """
        Initialize Bedrock client
        Uses AWS credential chain automatically (IAM role, environment variables, etc.)
        
        Args:
            region_name: AWS region (default: us-east-1)
        """
        try:
            # Initialize boto3 client for Bedrock
            # Automatically uses IAM role on EC2, or environment variables
            self.client = boto3.client('bedrock-runtime', region_name=region_name)
            
            logger.info(f"Bedrock client initialized successfully for region: {region_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    
    def invoke_claude(self, prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
                     max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Invoke Claude model
        
        Args:
            prompt: Input prompt
            model_id: Claude model ID
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            # Claude request format
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            generated_text = response_body.get('content', [{}])[0].get('text', '')
            
            logger.info(f"Claude response generated successfully, tokens: {len(generated_text.split())}")
            return generated_text
            
        except ClientError as e:
            logger.error(f"Claude API error: {e}")
            return f"Error calling Claude API: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in Claude call: {e}")
            return f"Unexpected error: {e}"
    
    def invoke_titan(self, prompt: str, model_id: str = "amazon.titan-text-express-v1",
                   max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Invoke Titan model
        
        Args:
            prompt: Input prompt
            model_id: Titan model ID
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            # Titan request format
            request_body = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": temperature,
                    "stopSequences": []
                }
            }
            
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            generated_text = response_body.get('results', [{}])[0].get('outputText', '')
            
            logger.info(f"Titan response generated successfully")
            return generated_text
            
        except ClientError as e:
            logger.error(f"Titan API error: {e}")
            return f"Error calling Titan API: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in Titan call: {e}")
            return f"Unexpected error: {e}"
    
    def invoke_llama(self, prompt: str, model_id: str = "meta.llama3-8b-instruct-v1:0",
                    max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Invoke Llama model
        
        Args:
            prompt: Input prompt
            model_id: Llama model ID
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            # Llama request format
            request_body = {
                "prompt": prompt,
                "max_gen_len": max_tokens,
                "temperature": temperature,
                "top_p": 0.9
            }
            
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response.get('body').read())
            generated_text = response_body.get('generation', '')
            
            logger.info(f"Llama response generated successfully")
            return generated_text
            
        except ClientError as e:
            logger.error(f"Llama API error: {e}")
            return f"Error calling Llama API: {e}"
        except Exception as e:
            logger.error(f"Unexpected error in Llama call: {e}")
            return f"Unexpected error: {e}"
    
    def generate_rag_response(self, query: str, documents: List[Dict], 
                            model_type: str = "claude") -> str:
        """
        Generate RAG response based on query and retrieved documents
        
        Args:
            query: User query
            documents: Retrieved documents with similarity scores
            model_type: Model type to use ('claude', 'titan', 'llama')
            
        Returns:
            Generated response
        """
        if not documents:
            return "I apologize, but I couldn't find any relevant information to answer your question. Please try rephrasing your query or using different keywords."
        
        # Prepare context from documents
        context_parts = []
        for i, doc in enumerate(documents[:5], 1):  # Use top 5 documents
            context_parts.append(f"""
Document {i}:
Title: {doc.get('title', 'Untitled')}
Category: {doc.get('category', 'Unknown')}
Similarity: {doc.get('similarity', 0):.1%}
Content: {doc.get('content', '')[:500]}...
""")
        
        context = "\n".join(context_parts)
        
        # Create prompt for RAG
        prompt = f"""You are a helpful AI assistant. Based on the following retrieved documents, please answer the user's question accurately and comprehensively.

User Question: {query}

Retrieved Documents:
{context}

Instructions:
1. Use only the information from the provided documents to answer the question
2. If the documents don't contain enough information, say so clearly
3. Cite the document numbers when referencing specific information
4. Provide a clear, concise, and helpful response
5. If multiple documents provide relevant information, synthesize them

Answer:"""

        # Choose model based on model_type
        if model_type.lower() == "claude":
            return self.invoke_claude(prompt)
        elif model_type.lower() == "titan":
            return self.invoke_titan(prompt)
        elif model_type.lower() == "llama":
            return self.invoke_llama(prompt)
        else:
            logger.warning(f"Unknown model type: {model_type}, defaulting to Claude")
            return self.invoke_claude(prompt)
    
    def test_connection(self, model_type: str = "claude") -> bool:
        """
        Test connection to Bedrock
        
        Args:
            model_type: Model type to test
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_prompt = "Hello, this is a test. Please respond with 'Connection successful'."
            
            if model_type.lower() == "claude":
                response = self.invoke_claude(test_prompt, max_tokens=50)
            elif model_type.lower() == "titan":
                response = self.invoke_titan(test_prompt, max_tokens=50)
            elif model_type.lower() == "llama":
                response = self.invoke_llama(test_prompt, max_tokens=50)
            else:
                logger.error(f"Unknown model type for test: {model_type}")
                return False
            
            logger.info(f"Bedrock connection test successful. Response: {response[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Bedrock connection test failed: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Configuration - uses default AWS credential chain
    AWS_REGION = "us-east-1"
    
    try:
        # Initialize service - automatically uses IAM role on EC2 or environment variables
        bedrock_service = BedrockLLMService(region_name=AWS_REGION)
        
        # Test connection
        print("Testing Bedrock connection...")
        if bedrock_service.test_connection("claude"):
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
        
        # Test RAG response
        test_documents = [
            {
                'title': 'Employee Onboarding Process',
                'content': 'New employees must complete orientation, set up payroll, and receive IT equipment within their first week.',
                'category': 'HR',
                'similarity': 0.85
            }
        ]
        
        print("\nTesting RAG response...")
        response = bedrock_service.generate_rag_response(
            "What is the onboarding process for new employees?",
            test_documents,
            model_type="claude"
        )
        print(f"RAG Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please check your AWS credentials and Bedrock access.")