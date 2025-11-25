import os
import json
import logging
import requests
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KimiLLMService:
    """
    Kimi LLM Service wrapper for Confluence Finder
    """
    
    def __init__(self):
        self.api_key = os.getenv('KIMI_API_KEY')
        self.api_base = os.getenv('KIMI_API_BASE', 'https://api.moonshot.cn/v1')
        self.default_model = os.getenv('KIMI_MODEL', 'moonshot-v1-8k')
        self.session = requests.Session()
        
    def generate_rag_response(self, query: str, search_results: list) -> Optional[str]:
        """
        Generate answer using Kimi LLM with RAG enhancement
        
        Args:
            query: User's question
            search_results: List of search results from vector database
        """
        try:
            if not self.api_key:
                logger.warning("KIMI_API_KEY not set, skipping Kimi LLM call")
                return "Kimi LLM API key not configured"
            
            # Build context from search results
            context_parts = []
            for i, result in enumerate(search_results, 1):
                if isinstance(result, dict):
                    content = result.get('content', '')
                    title = result.get('title', f'Document {i}')
                    score = result.get('similarity_score', 0)
                    
                    if content:
                        context_parts.append(f"Document {i} (Title: {title}, Similarity: {score:.3f}):\n{content[:500]}...")
            
            context_text = "\n\n".join(context_parts) if context_parts else "No relevant documents found."
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            system_prompt = """You are a helpful assistant that answers questions based on provided documentation. 

When answering:
1. Use the provided documentation as your primary source of information
2. If the documentation doesn't contain the answer, clearly state that
3. Provide specific references to which documents support your answer
4. Be concise but comprehensive
5. If multiple documents provide relevant information, synthesize them

Always cite the document number(s) you're referencing in your answer."""
            
            user_prompt = f"""Based on the following documentation, please answer this question: {query}

Relevant Documentation:
{context_text}

Please provide a comprehensive answer based on the documentation above."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            payload = {
                "model": self.default_model,
                "messages": messages,
                "temperature": 0.1,  # Lower temperature for more factual responses
                "max_tokens": 2000
            }
            
            logger.info(f"Calling Kimi LLM API with prompt length: {len(user_prompt)}")
            response = self.session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.error(f"Kimi LLM API error: {response.status_code} - {response.text}")
                return f"Error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Exception in Kimi LLM call: {str(e)}")
            return f"Exception: {str(e)}"
    
    def get_status(self) -> Dict[str, any]:
        """
        Check if Kimi LLM service is configured
        """
        return {
            "configured": bool(self.api_key),
            "model": self.default_model,
            "api_base": self.api_base
        }