import React, { useState } from 'react'
import { Search, FileText, Bot, User, ExternalLink, Loader2, Settings } from 'lucide-react'
import axios from 'axios'
import AdminPanel from './components/AdminPanel'

interface SearchResult {
  title: string
  content: string
  url: string
  score: number
  answer?: string
}

export default function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showAdmin, setShowAdmin] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError('')
    setResults([])

    try {
      const response = await axios.post('http://localhost:5000/search', { query }, {
        headers: {
          'Content-Type': 'application/json;charset=UTF-8'
        }
      })
      setResults(response.data.results)
    } catch (err: any) {
      setError(err.response?.data?.error || '搜索失败，请稍后重试')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <FileText className="w-10 h-10 text-primary-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900">Confluence Finder</h1>
            <button
              onClick={() => setShowAdmin(!showAdmin)}
              className="ml-4 p-2 text-gray-500 hover:text-primary-600 transition-colors"
              title="管理面板"
            >
              <Settings className="w-6 h-6" />
            </button>
          </div>
          <p className="text-lg text-gray-600">AI驱动的智能文档查找系统</p>
        </header>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-8">
          <div className="relative max-w-3xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="输入你的问题，比如：如何申请年假？"
                className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent shadow-sm"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    搜索中
                  </>
                ) : (
                  '搜索'
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Admin Panel */}
        {showAdmin && (
          <div className="mb-8">
            <AdminPanel />
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="max-w-3xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Results */}
        {results.length > 0 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">搜索结果</h2>
            {results.map((result, index) => (
              <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-primary-500 mr-2" />
                    <h3 className="text-lg font-semibold text-gray-900">{result.title}</h3>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500">相关度: {Math.round(result.score * 100)}%</span>
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:text-primary-700"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                </div>
                
                {result.answer && (
                  <div className="mb-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                    <div className="flex items-center mb-2">
                      <Bot className="w-4 h-4 text-blue-600 mr-2" />
                      <span className="text-sm font-medium text-blue-800">AI回答</span>
                    </div>
                    <p className="text-gray-700">{result.answer}</p>
                  </div>
                )}
                
                <div className="text-gray-600">
                  <p className="line-clamp-3">{result.content}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && results.length === 0 && !error && (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">输入问题开始搜索Confluence文档</p>
          </div>
        )}
      </div>
    </div>
  )
}