# Confluence Finder 开发指南

## 🎯 项目概述

这是一个为期一周开发的AI驱动Confluence文档查找系统，旨在解决企业内部Confluence文档难以查找的问题。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React前端     │    │   Python后端    │    │  Confluence API │
│                 │    │                 │    │                 │
│ - 用户界面      │◄──►│ - 搜索API       │◄──►│ - 文档获取      │
│ - 结果展示      │    │ - AI问答        │    │ - 空间管理      │
│ - 管理面板      │    │ - 向量搜索      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ChromaDB      │
                       │                 │
                       │ - 向量存储      │
                       │ - 语义搜索      │
                       │ - 文档索引      │
                       └─────────────────┘
```

## 🚀 快速开始

### 1. 环境准备

**必需软件：**
- Node.js 16+
- Python 3.8+
- OpenAI API Key
- Confluence访问权限

### 2. 配置步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd confluence_finder
```

2. **安装依赖**
```bash
npm run install:all
```

3. **配置环境变量**
```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`：
```env
OPENAI_API_KEY=your_openai_api_key
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_USERNAME=your_email@example.com
CONFLUENCE_API_TOKEN=your_api_token
```

4. **启动应用**
```bash
# Windows
start.bat

# Linux/Mac
./deploy.sh
npm run dev
```

## 🔧 核心功能

### 1. 智能搜索
- 基于语义的文档检索
- AI驱动的答案生成
- 相关度评分排序

### 2. 文档索引
- 自动从Confluence同步文档
- 智能文本分块处理
- 向量化存储

### 3. 用户界面
- 现代化React界面
- 响应式设计
- 实时搜索反馈

## 📁 项目结构

```
confluence_finder/
├── frontend/                 # React前端
│   ├── src/
│   │   ├── components/      # React组件
│   │   ├── App.tsx         # 主应用
│   │   └── main.tsx        # 入口文件
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # Python后端
│   ├── app.py              # Flask应用
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量模板
├── docs/                   # 文档
├── start.bat              # Windows启动脚本
├── deploy.sh              # Linux部署脚本
└── README.md
```

## 🛠️ 开发指南

### 前端开发
```bash
cd frontend
npm run dev    # 开发服务器
npm run build  # 生产构建
```

### 后端开发
```bash
cd backend
python app.py  # 启动Flask服务器
```

### API接口

**搜索文档**
```
POST /api/search
{
  "query": "如何申请年假？"
}
```

**索引文档**
```
POST /api/index
```

## 🔍 技术细节

### 向量搜索
- 使用 `SentenceTransformer` 生成文档嵌入
- ChromaDB 存储和检索向量
- 余弦相似度计算相关度

### AI问答
- OpenAI GPT-3.5-turbo 模型
- 基于检索到的文档生成答案
- 支持上下文对话

### 文档处理
- HTML内容清理
- 智能文本分块
- Token限制管理

## 📈 性能优化

1. **缓存策略**
   - 文档嵌入缓存
   - 搜索结果缓存

2. **数据库优化**
   - 向量索引优化
   - 批量处理

3. **前端优化**
   - 组件懒加载
   - 搜索防抖

## 🚨 注意事项

1. **API限制**
   - OpenAI API调用限制
   - Confluence API速率限制

2. **安全性**
   - API密钥安全存储
   - 用户权限验证

3. **扩展性**
   - 支持多数据源
   - 分布式部署

## 🎨 UI/UX设计原则

1. **简洁性** - 清晰的视觉层次
2. **响应性** - 适配各种设备
3. **可访问性** - 无障碍设计
4. **反馈性** - 实时状态提示

## 🏆 比赛优势

1. **技术创新** - AI+向量搜索
2. **实用价值** - 解决实际痛点
3. **用户体验** - 简单易用
4. **可扩展性** - 支持企业级部署

## 📞 技术支持

如有问题，请检查：
1. 环境变量配置
2. API密钥有效性
3. 网络连接状态
4. 依赖包版本

---

祝比赛顺利！🎉