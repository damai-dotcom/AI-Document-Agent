import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
  isTyping?: boolean
}

interface SearchResult {
  title: string
  content: string
  url: string
  score: number
}

export default function CoreApp() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])

  // Auto scroll to the latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Typewriter effect
  const typewriterEffect = (
    text: string,
    callback: (displayText: string) => void
  ) => {
    let index = 0

    // Immediate initial update
    callback(text.substring(0, index))

    const interval = setInterval(() => {
      index++
      if (index > text.length) {
        clearInterval(interval)
        return
      }
      callback(text.substring(0, index))
    }, 20) // Adjust speed, smaller value is faster

    return interval
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    // Add user message
    const userMessage: Message = { role: 'user', content: query }
    setMessages((prev) => [...prev, userMessage])

    // Add assistant message placeholder
    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
      isTyping: true,
    }
    setMessages((prev) => [...prev, assistantMessage])

    setIsLoading(true)
    setError('')
    setSearchResults([])

    try {
      const response = await axios.post('http://localhost:5000/api/search', {
        query,
      })

      // Save search results
      setSearchResults(response.data.results || [])

      // Get AI answer
      const aiAnswer =
        response.data.results[0]?.answer ||
        'Sorry, I cannot answer this question.'

      // Use typewriter effect to display AI answer
      const interval = typewriterEffect(aiAnswer, (displayText) => {
        setMessages((prev) => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            content: displayText,
            isTyping: true, // Keep as true until typing is complete
          }
          return newMessages
        })
      })

      // Ensure complete display and clean up
      const totalDuration = Math.max(aiAnswer.length * 20, 1000) // Minimum 1 second
      setTimeout(() => {
        clearInterval(interval)
        // Force update to show the complete answer
        setMessages((prev) => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1] = {
            ...newMessages[newMessages.length - 1],
            content: aiAnswer, // Ensure full content is displayed
            isTyping: false,
          }
          return newMessages
        })
      }, totalDuration)
    } catch (err: any) {
      setError(err.message || 'Search failed')
      // Remove assistant message placeholder
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setIsLoading(false)
      setQuery('') // Clear input box
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center">
          <div className="flex items-center space-x-2">
            <Bot className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-semibold text-gray-900">
              Confluence Finder
            </h1>
          </div>
          <div className="ml-auto text-sm text-gray-500">
            AI-powered intelligent document search system
          </div>
        </div>
      </header>

      {/* Message Area */}
      <main className="flex-1 overflow-y-auto custom-scrollbar">
        <div className="max-w-4xl mx-auto px-4 py-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h2 className="text-2xl font-semibold text-gray-700 mb-2">
                How can I help you today?
              </h2>
              <p className="text-gray-500">
                You can ask any questions about company documents, policies, or
                procedures
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  }`}>
                  <div
                    className={`flex items-start space-x-3 max-w-3xl ${
                      message.role === 'user'
                        ? 'flex-row-reverse space-x-reverse'
                        : ''
                    }`}>
                    <div
                      className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'user' ? 'bg-blue-600' : 'bg-gray-200'
                      }`}>
                      {message.role === 'user' ? (
                        <User className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-gray-600" />
                      )}
                    </div>
                    <div
                      className={`px-4 py-3 rounded-lg message-fade-in ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white border border-gray-200 text-gray-800'
                      }`}>
                      {message.isTyping && (
                        <div className="flex items-center space-x-1 mb-1">
                          <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
                          <span className="text-sm text-gray-500">
                            Typing...
                          </span>
                        </div>
                      )}
                      <p
                        className={`whitespace-pre-wrap ${
                          message.isTyping ? 'typing-cursor' : ''
                        }`}>
                        {message.content}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Search Results Display */}
          {searchResults.length > 0 && messages.length > 0 && (
            <div className="mt-8 bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">
                Retrieved Documents
              </h3>
              <div className="space-y-3">
                {searchResults.slice(0, 3).map((result, index) => (
                  <div
                    key={index}
                    className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="flex justify-between items-start mb-1">
                      <h4 className="font-medium text-gray-900">
                        {result.title}
                      </h4>
                      <span className="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded">
                        {Math.round(result.score * 100)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {result.content}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-600">❌ {error}</p>
            </div>
          )}
        </div>
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t border-gray-200 px-4 py-4">
        <form onSubmit={handleSearch} className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your question..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={1}
                disabled={isLoading}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSearch(e)
                  }
                }}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center">
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Press Enter to send, Shift + Enter for new line
          </p>
        </form>
      </footer>
    </div>
  )
}
