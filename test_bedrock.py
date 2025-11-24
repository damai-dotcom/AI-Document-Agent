#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Bedrock LLM Integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bedrock_llm import BedrockLLMService
from config import Config

def test_bedrock_connection():
    """Test Bedrock connection and basic functionality"""
    print("🧪 Testing Bedrock LLM Integration...")
    print("=" * 50)
    
    try:
        # Initialize Bedrock service (uses IAM role or environment variables)
        bedrock_service = BedrockLLMService(region_name=Config.AWS_REGION)
        
        print(f"✅ Bedrock client initialized for region: {Config.AWS_REGION}")
        
        # Test connection with Claude
        print("\n🔍 Testing Claude model...")
        claude_response = bedrock_service.invoke_claude(
            "Hello! Please respond with 'Claude is working correctly.'",
            max_tokens=50
        )
        print(f"Claude response: {claude_response}")
        
        # Test RAG functionality
        print("\n📚 Testing RAG response generation...")
        test_documents = [
            {
                'title': 'Employee Onboarding Process',
                'content': 'New employees must complete orientation, set up payroll, and receive IT equipment within their first week. The onboarding process includes security training, system access setup, and team introduction.',
                'category': 'HR',
                'similarity': 0.85
            },
            {
                'title': 'IT Equipment Policy',
                'content': 'All employees receive a laptop, monitor, and mobile phone. IT equipment must be returned upon termination of employment. Damaged equipment should be reported to IT support immediately.',
                'category': 'IT',
                'similarity': 0.72
            }
        ]
        
        rag_response = bedrock_service.generate_rag_response(
            "What equipment do new employees receive?",
            test_documents,
            model_type="claude"
        )
        
        print(f"RAG Response: {rag_response}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure AWS credentials are configured (IAM role or environment variables)")
        print("2. Check if Bedrock service is available in your region")
        print("3. Verify IAM permissions for bedrock:InvokeModel")
        print("4. Confirm the model is available in your AWS account")
        return False

def test_config():
    """Test configuration"""
    print("⚙️  Testing configuration...")
    print(f"Region: {Config.AWS_REGION}")
    print(f"Model Type: {Config.BEDROCK_MODEL_TYPE}")
    print(f"Claude Model ID: {Config.CLAUDE_MODEL_ID}")
    print(f"Max Tokens: {Config.MAX_TOKENS}")
    print(f"Temperature: {Config.TEMPERATURE}")
    print("✅ Configuration loaded successfully\n")

if __name__ == "__main__":
    print("🚀 Bedrock LLM Integration Test")
    print("=" * 50)
    
    # Test configuration
    test_config()
    
    # Test Bedrock functionality
    success = test_bedrock_connection()
    
    if success:
        print("\n🎉 Bedrock LLM is ready for integration!")
        print("You can now start the main service with: python start.py")
    else:
        print("\n⚠️  Please fix the issues above before using the main service.")
        sys.exit(1)