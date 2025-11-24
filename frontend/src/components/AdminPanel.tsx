import React, { useState, useEffect } from 'react'
import { Database, RefreshCw, CheckCircle, AlertCircle, Loader2, Info, FileText } from 'lucide-react'
import axios from 'axios'

interface SystemStatus {
  data_exported: boolean
  export_info?: {
    export_time: string
    total_docs: number
    file_size: number
  }
  collection_stats?: {
    total_documents: number
    collection_name: string
  }
  llm_type: string
}

export default function AdminPanel() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    fetchSystemStatus()
  }, [])

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get('/api/status')
      setSystemStatus(response.data)
    } catch (error) {
      console.error('获取系统状态失败:', error)
    }
  }

  const formatFileSize = (bytes: number) => {
    return (bytes / 1024).toFixed(2) + ' KB'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN')
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center mb-4">
        <Database className="w-6 h-6 text-primary-600 mr-2" />
        <h2 className="text-xl font-semibold text-gray-900">系统状态</h2>
        <button
          onClick={fetchSystemStatus}
          className="ml-auto p-2 text-gray-500 hover:text-primary-600 transition-colors"
          title="刷新状态"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
      
      {systemStatus && (
        <div className="space-y-4">
          {/* 数据状态 */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center mb-3">
              <FileText className="w-5 h-5 text-blue-600 mr-2" />
              <h3 className="font-medium text-gray-900">本地数据状态</h3>
            </div>
            
            {systemStatus.data_exported ? (
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">导出状态:</span>
                  <span className="text-green-600 font-medium">✅ 已导出</span>
                </div>
                {systemStatus.export_info && (
                  <>
                    <div className="flex justify-between">
                      <span className="text-gray-600">导出时间:</span>
                      <span className="text-gray-900">{formatDate(systemStatus.export_info.export_time)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">文档数量:</span>
                      <span className="text-gray-900">{systemStatus.export_info.total_docs}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">文件大小:</span>
                      <span className="text-gray-900">{formatFileSize(systemStatus.export_info.file_size)}</span>
                    </div>
                  </>
                )}
                {systemStatus.collection_stats && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">向量条目:</span>
                    <span className="text-gray-900">{systemStatus.collection_stats.total_documents}</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-4">
                <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-2" />
                <p className="text-gray-600 text-sm mb-3">本地数据不存在</p>
                <p className="text-xs text-gray-500">请运行数据导入工具导入Confluence文档</p>
              </div>
            )}
          </div>

          {/* AI配置状态 */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center mb-3">
              <Info className="w-5 h-5 text-purple-600 mr-2" />
              <h3 className="font-medium text-gray-900">AI配置</h3>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">LLM类型:</span>
              <span className="text-gray-900 font-medium">{systemStatus.llm_type.toUpperCase()}</span>
            </div>
          </div>

          {/* 操作说明 */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h4 className="font-medium text-blue-900 mb-2">数据导入说明</h4>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>配置 backend/.env 中的Confluence API信息</li>
              <li>运行 <code className="bg-blue-100 px-1 rounded">python import_data.py</code></li>
              <li>选择操作3进行完整导入</li>
              <li>导入完成后刷新此页面查看状态</li>
            </ol>
          </div>
        </div>
      )}
      
      {isLoading && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="w-6 h-6 animate-spin text-primary-600 mr-2" />
          <span className="text-gray-600">加载中...</span>
        </div>
      )}
    </div>
  )
}