# Confluence Finder - 简化版

一个支持中英文语义检索的文档查找系统，使用 RAG 架构。

## 核心功能

- ✅ 支持中英文语义检索
- ✅ 使用 paraphrase-multilingual-MiniLM-L12-v2 模型
- ✅ ChromaDB 向量数据库
- ✅ Mock LLM 响应（可替换为真实LLM）
- ✅ 简洁的Web界面

## 文件结构

```
confluence_finder/
├── rag_service.py            # 主服务文件
├── init_data.py              # 数据初始化脚本
├── requirements.txt          # 依赖包
├── data/
│   └── confluence_export.json  # 文档数据
├── chroma_db/               # 向量数据库
└── model_cache/            # 模型缓存
```

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 初始化数据
```bash
python init_data.py
```

### 3. 启动服务
```bash
python rag_service.py
```

### 4. 访问界面
打开浏览器访问: http://localhost:5001

## API 接口

- `GET /` - 测试界面
- `POST /search` - 文档搜索
- `GET /stats` - 统计信息
- `GET /health` - 健康检查

### 搜索接口示例
```json
POST /search
{
    "query": "员工入职流程"
}
```

响应:
```json
{
    "success": true,
    "query": "员工入职流程",
    "documents": [...],
    "llm_response": "...",
    "total": 3
}
```

## 技术栈

- **语义模型**: paraphrase-multilingual-MiniLM-L12-v2
- **向量数据库**: ChromaDB
- **Web框架**: Flask
- **前端**: 原生HTML/CSS/JavaScript

## 特性

1. **中英文支持**: 使用多语言模型，支持中英文语义检索
2. **语义搜索**: 基于向量相似度的语义匹配
3. **简洁架构**: 代码简洁，易于维护和扩展
4. **Mock LLM**: 提供模拟LLM响应，可轻松替换为真实LLM

## 清理说明

这个简化版本移除了以下内容：
- 多余的测试文件
- 备份文件
- 复杂的配置
- 不必要的依赖
- 冗余的代码逻辑

保留了核心的语义检索功能，代码更简洁易维护。