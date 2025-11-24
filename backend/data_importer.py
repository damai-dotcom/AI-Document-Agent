"""
Confluence文档数据导入工具
用于一次性将Confluence文档导入到本地向量库
"""
import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import tiktoken
import logging
from datetime import datetime

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfluenceDataImporter:
    def __init__(self):
        self.base_url = os.getenv('CONFLUENCE_URL')
        self.username = os.getenv('CONFLUENCE_USERNAME')
        self.api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.auth = (self.username, self.api_token)
        
        # 本地存储路径
        self.data_dir = './data'
        self.export_file = os.path.join(self.data_dir, 'confluence_export.json')
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # 初始化ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=os.getenv('CHROMA_DB_PATH', './chroma_db'))
        self.collection = self.chroma_client.get_or_create_collection(name="confluence_docs")
    
    def get_spaces(self):
        """获取所有空间"""
        try:
            url = f"{self.base_url}/wiki/rest/api/space"
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取空间失败: {str(e)}")
            return None
    
    def get_pages_in_space(self, space_key, limit=100):
        """获取空间中的所有页面"""
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
            logger.error(f"获取页面失败: {str(e)}")
            return None
    
    def get_page_content(self, page_id):
        """获取页面内容"""
        try:
            url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
            params = {'expand': 'body.view,version'}
            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取页面内容失败: {str(e)}")
            return None
    
    def clean_html_content(self, html_content):
        """清理HTML内容，提取纯文本"""
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(strip=True)
    
    def chunk_text(self, text, max_tokens=800):
        """将文本分块，避免超出token限制"""
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
        """导出所有Confluence文档到本地JSON文件"""
        logger.info("开始导出Confluence文档...")
        
        all_docs = []
        spaces = self.get_spaces()
        
        if not spaces:
            logger.error("无法获取空间信息")
            return False
        
        for space in spaces.get('results', []):
            space_key = space.get('key')
            space_name = space.get('name', space_key)
            logger.info(f"正在处理空间: {space_name} ({space_key})")
            
            pages = self.get_pages_in_space(space_key)
            if not pages:
                continue
            
            for page in pages.get('results', []):
                page_id = page.get('id')
                page_title = page.get('title', '')
                
                logger.info(f"正在导出页面: {page_title}")
                
                page_data = self.get_page_content(page_id)
                if not page_data:
                    continue
                
                content = self.clean_html_content(
                    page_data.get('body', {}).get('view', {}).get('value', '')
                )
                url = f"{self.base_url}/wiki/pages/viewpage.action?pageId={page_id}"
                
                # 保存完整文档信息
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
        
        # 保存到本地文件
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_docs': len(all_docs),
            'docs': all_docs
        }
        
        with open(self.export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功导出 {len(all_docs)} 个文档到 {self.export_file}")
        return True
    
    def import_to_vector_db(self):
        """从本地JSON文件导入到向量数据库"""
        if not os.path.exists(self.export_file):
            logger.error(f"导出文件不存在: {self.export_file}")
            return False
        
        logger.info("开始导入文档到向量数据库...")
        
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
            
            # 分块处理
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
        
        # 生成嵌入
        logger.info("正在生成文档嵌入...")
        embeddings = self.embedding_model.encode(documents)
        
        # 清空现有集合
        try:
            self.collection.delete()
            self.collection = self.chroma_client.get_or_create_collection(name="confluence_docs")
        except:
            pass
        
        # 添加到ChromaDB
        logger.info("正在保存到向量数据库...")
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"成功导入 {len(documents)} 个文档块到向量数据库")
        return True
    
    def full_import(self):
        """完整导入流程：导出文档 + 导入向量库"""
        logger.info("开始完整导入流程...")
        
        # 1. 导出文档到本地
        if not self.export_all_docs():
            logger.error("文档导出失败")
            return False
        
        # 2. 导入到向量数据库
        if not self.import_to_vector_db():
            logger.error("向量数据库导入失败")
            return False
        
        logger.info("完整导入流程完成！")
        return True

def main():
    """主函数"""
    importer = ConfluenceDataImporter()
    
    print("Confluence文档导入工具")
    print("1. 导出文档到本地")
    print("2. 从本地导入向量库")
    print("3. 完整导入")
    
    choice = input("请选择操作 (1/2/3): ").strip()
    
    if choice == '1':
        importer.export_all_docs()
    elif choice == '2':
        importer.import_to_vector_db()
    elif choice == '3':
        importer.full_import()
    else:
        print("无效选择")

if __name__ == "__main__":
    main()