import React, { useState } from 'react'
import { Search, FileText, Bot, Loader2 } from 'lucide-react'
import axios from 'axios'

interface SearchResult {
  title: string
  content: string
  url: string
  similarity: number
}

interface SearchResponse {
  success: boolean
  query: string
  documents: SearchResult[]
  llm_response: string
  llm_input: string
  total: number
}

export default function CoreApp() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError('')
    setResults(null)

    try {
      const response = await axios.post('http://localhost:5000/search', { query })
      setResults(response.data)
    } catch (err: any) {
      setError(err.message || '搜索失败')
    } finally {
      setIsLoading(false)
    }
  }

  const quickQueries = [
    '入职资料有吗，我需要看',
    '我刚入职，有什么资料',
    '员工请假制度',
    'onboarding documents'
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-blue-600">
          🚀 语义搜索系统
        </h1>

        {/* 搜索框 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <form onSubmit={handleSearch} className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="输入您的问题，例如：入职资料有吗，我需要看"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              {isLoading ? '搜索中...' : '搜索'}
            </button>
          </form>
        </div>

        {/* 快速测试 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-3">🎯 快速测试</h3>
          <div className="flex flex-wrap gap-2">
            {quickQueries.map((q, index) => (
              <button
                key={index}
                onClick={() => setQuery(q)}
                className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 text-sm transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            ❌ {error}
          </div>
        )}

        {/* 搜索结果 */}
        {results && (
          <div className="space-y-6">
            {/* 检索到的文档 */}
            {results.documents.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  检索到的文档 ({results.documents.length})
                </h2>
                <div className="space-y-4">
                  {results.documents.map((doc, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-blue-600">{doc.title}</h3>
                        <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          相似度: {(doc.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-gray-600">{doc.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* LLM回答 */}
            {results.llm_response && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Bot className="w-5 h-5" />
                  AI回答
                </h2>
                <div className="prose max-w-none">
                  <pre className="whitespace-pre-wrap text-gray-700 font-sans">
                    {results.llm_response}
                  </pre>
                </div>
              </div>
            )}

            {/* 发送给LLM的完整内容 */}
            {results.llm_input && (
              <div className="bg-gray-50 rounded-lg p-6">
                <h2 className="text-xl font-semibold mb-4">📤 发送给LLM的内容</h2>
                <pre className="text-sm bg-gray-100 p-4 rounded overflow-x-auto whitespace-pre-wrap">
                  {results.llm_input}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}