"""
Confluence Finder - 本地化版本
所有文档数据存储在本地，仅调用外部LLM进行问答
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

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置OpenAI (仅用于问答)
openai.api_key = os.getenv('OPENAI_API_KEY')

# 配置本地ChromaDB
chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_DB_PATH', './chroma_db'))
collection = chroma_client.get_or_create_collection(name="confluence_docs")

# 初始化本地嵌入模型
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# 本地数据文件路径
DATA_DIR = './data'
EXPORT_FILE = os.path.join(DATA_DIR, 'confluence_export.json')

class LocalVectorSearch:
    """本地向量搜索引擎"""
    
    def __init__(self):
        self.collection = collection
        self.embedding_model = embedding_model
    
    def search_documents(self, query, n_results=5):
        """搜索相关文档"""
        try:
            # 生成查询嵌入
            query_embedding = self.embedding_model.encode([query])
            
            # 搜索相似文档
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results
            )
            
            return results
        except Exception as e:
            logger.error(f"搜索文档时出错: {str(e)}")
            return None
    
    def get_collection_stats(self):
        """获取集合统计信息"""
        try:
            count = self.collection.count()
            return {
                'total_documents': count,
                'collection_name': self.collection.name
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return None

class AIAnswerGenerator:
    """AI答案生成器 - 仅调用外部LLM"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        
        # 支持多种LLM接口
        self.llm_type = os.getenv('LLM_TYPE', 'openai')  # openai, claude, local
        
    def generate_answer(self, query, context_docs):
        """使用外部LLM生成答案"""
        try:
            context = "\n\n".join([f"文档片段{i+1}: {doc}" for i, doc in enumerate(context_docs)])
            
            if self.llm_type == 'openai':
                return self._generate_with_openai(query, context)
            elif self.llm_type == 'claude':
                return self._generate_with_claude(query, context)
            else:
                return self._generate_with_openai(query, context)
                
        except Exception as e:
            logger.error(f"生成答案时出错: {str(e)}")
            return None
    
    def _generate_with_openai(self, query, context):
        """使用OpenAI生成答案"""
        prompt = f"""你是一个专业的文档助手。请基于以下Confluence文档内容回答用户问题。

文档内容:
{context}

用户问题: {query}

回答要求:
1. 基于提供的文档内容回答
2. 如果文档中没有相关信息，请诚实说明
3. 回答要准确、简洁、有用
4. 可以适当引用文档内容

回答:"""
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的企业文档助手，擅长基于提供的文档内容回答用户问题。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_with_claude(self, query, context):
        """使用Claude生成答案（预留接口）"""
        # 这里可以集成Claude API
        return self._generate_with_openai(query, context)

class DataManager:
    """本地数据管理器"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.export_file = EXPORT_FILE
    
    def get_export_info(self):
        """获取导出信息"""
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
            logger.error(f"读取导出信息失败: {str(e)}")
            return None
    
    def check_data_exists(self):
        """检查本地数据是否存在"""
        return os.path.exists(self.export_file)

# 初始化组件
vector_search = LocalVectorSearch()
ai_generator = AIAnswerGenerator()
data_manager = DataManager()

@app.route('/api/search', methods=['POST'])
def search():
    """搜索API - 完全本地化搜索 + 外部LLM问答"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': '查询不能为空'}), 400
        
        # 检查本地数据是否存在
        if not data_manager.check_data_exists():
            return jsonify({'error': '本地数据不存在，请先导入文档'}), 400
        
        # 本地向量搜索
        search_results = vector_search.search_documents(query)
        
        if not search_results:
            return jsonify({'error': '搜索失败'}), 500
        
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results['distances'][0]
        
        # 使用外部LLM生成答案
        answer = ai_generator.generate_answer(query, documents[:3])
        
        # 构建结果
        results = []
        for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
            # 计算相关度分数 (0-1)
            score = 1 / (1 + distance)
            
            result = {
                'title': metadata['title'],
                'content': doc,
                'url': metadata['url'],
                'score': score,
                'space_key': metadata.get('space_key', ''),
                'chunk_index': metadata.get('chunk_index', 0)
            }
            
            # 只在第一个结果中添加AI答案
            if i == 0 and answer:
                result['answer'] = answer
            
            results.append(result)
        
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"搜索API出错: {str(e)}")
        return jsonify({'error': '搜索失败，请稍后重试'}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """系统状态API"""
    try:
        # 检查数据状态
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
        logger.error(f"状态检查出错: {str(e)}")
        return jsonify({'error': '状态检查失败'}), 500

@app.route('/api/import/status', methods=['GET'])
def import_status():
    """导入状态API"""
    try:
        if data_manager.check_data_exists():
            export_info = data_manager.get_export_info()
            collection_stats = vector_search.get_collection_stats()
            
            return jsonify({
                'data_exists': True,
                'export_info': export_info,
                'collection_stats': collection_stats,
                'message': '本地数据已就绪'
            })
        else:
            return jsonify({
                'data_exists': False,
                'message': '本地数据不存在，请运行数据导入工具'
            })
            
    except Exception as e:
        logger.error(f"检查导入状态出错: {str(e)}")
        return jsonify({'error': '检查失败'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """简单健康检查"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    
    logger.info("启动Confluence Finder服务器...")
    logger.info(f"本地数据目录: {DATA_DIR}")
    logger.info(f"向量数据库路径: {os.getenv('CHROMA_DB_PATH', './chroma_db')}")
    logger.info(f"LLM类型: {ai_generator.llm_type}")
    
    app.run(host='0.0.0.0', port=port, debug=True)