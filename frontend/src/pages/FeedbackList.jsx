import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import {
  FunnelIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  EyeIcon,
} from '@heroicons/react/24/outline'

import { feedbackAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

function FeedbackList() {
  const [filters, setFilters] = useState({
    page: 1,
    size: 20,
    search: '',
    channel: '',
    status: '',
    sentiment_label: '',
    flagged: null
  })

  const { data: feedbackData, isLoading, error } = useQuery(
    ['feedback-list', filters],
    () => feedbackAPI.getList(filters),
    {
      select: (response) => response.data,
      keepPreviousData: true
    }
  )

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filtering
    }))
  }

  const getSentimentColor = (sentiment, label) => {
    switch (label) {
      case 'positive':
        return 'text-success-600 bg-success-50'
      case 'negative':
        return 'text-danger-600 bg-danger-50'
      default:
        return 'text-neutral-600 bg-neutral-50'
    }
  }

  const getChannelColor = (channel) => {
    const colors = {
      web: 'text-blue-600 bg-blue-50',
      email: 'text-purple-600 bg-purple-50',
      whatsapp: 'text-green-600 bg-green-50',
      google_reviews: 'text-red-600 bg-red-50'
    }
    return colors[channel] || 'text-neutral-600 bg-neutral-50'
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (error) {
    return <ErrorMessage message="Failed to load feedback data" />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900">Feedback Management</h2>
          <p className="text-neutral-600 mt-1">
            View and manage all customer feedback
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl p-6 shadow-soft border border-neutral-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-neutral-900 flex items-center">
            <FunnelIcon className="h-5 w-5 mr-2" />
            Filters
          </h3>
          <button
            onClick={() => setFilters({ page: 1, size: 20, search: '', channel: '', status: '', sentiment_label: '', flagged: null })}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            Clear all
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-neutral-700 mb-2">Search</label>
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400" />
              <input
                type="text"
                placeholder="Search feedback..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="input-field pl-10"
              />
            </div>
          </div>

          {/* Channel */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Channel</label>
            <select
              value={filters.channel}
              onChange={(e) => handleFilterChange('channel', e.target.value)}
              className="input-field"
            >
              <option value="">All channels</option>
              <option value="web">Web</option>
              <option value="email">Email</option>
              <option value="whatsapp">WhatsApp</option>
              <option value="google_reviews">Google Reviews</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
              className="input-field"
            >
              <option value="">All statuses</option>
              <option value="new">New</option>
              <option value="reviewed">Reviewed</option>
              <option value="resolved">Resolved</option>
              <option value="escalated">Escalated</option>
            </select>
          </div>

          {/* Sentiment */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Sentiment</label>
            <select
              value={filters.sentiment_label}
              onChange={(e) => handleFilterChange('sentiment_label', e.target.value)}
              className="input-field"
            >
              <option value="">All sentiments</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>

          {/* Flagged */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">Priority</label>
            <select
              value={filters.flagged === null ? '' : filters.flagged.toString()}
              onChange={(e) => handleFilterChange('flagged', e.target.value === '' ? null : e.target.value === 'true')}
              className="input-field"
            >
              <option value="">All feedback</option>
              <option value="true">Flagged only</option>
              <option value="false">Non-flagged</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white rounded-2xl shadow-soft border border-neutral-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-neutral-200">
          <div className="flex items-center justify-between">
            <p className="text-sm text-neutral-600">
              Showing <span className="font-medium">{feedbackData?.items?.length || 0}</span> of{' '}
              <span className="font-medium">{feedbackData?.total || 0}</span> results
            </p>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-neutral-600">Page</span>
              <span className="font-medium">{feedbackData?.page || 1}</span>
              <span className="text-sm text-neutral-600">of</span>
              <span className="font-medium">{feedbackData?.pages || 1}</span>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-neutral-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Feedback
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Sentiment
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Channel
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-neutral-200">
              {feedbackData?.items?.map((feedback) => (
                <motion.tr
                  key={feedback.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="hover:bg-neutral-50 transition-colors"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-start space-x-3">
                      {feedback.flagged && (
                        <ExclamationTriangleIcon className="h-5 w-5 text-danger-500 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-neutral-900 line-clamp-2">
                          {feedback.text}
                        </p>
                        {feedback.guest_name && (
                          <p className="text-xs text-neutral-500 mt-1">
                            by {feedback.guest_name}
                          </p>
                        )}
                        {feedback.topics && feedback.topics.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {feedback.topics.slice(0, 2).map((topic, index) => (
                              <span
                                key={index}
                                className="text-xs px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full"
                              >
                                {topic}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSentimentColor(feedback.sentiment, feedback.sentiment_label)}`}>
                      {feedback.sentiment_label}
                      {feedback.sentiment && (
                        <span className="ml-1">({feedback.sentiment.toFixed(2)})</span>
                      )}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getChannelColor(feedback.channel)}`}>
                      {feedback.channel.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-neutral-100 text-neutral-800">
                      {feedback.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-neutral-500">
                    {new Date(feedback.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-primary-600 hover:text-primary-700 transition-colors">
                      <EyeIcon className="h-5 w-5" />
                    </button>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {feedbackData?.pages > 1 && (
          <div className="px-6 py-4 border-t border-neutral-200">
            <div className="flex items-center justify-between">
              <button
                onClick={() => handleFilterChange('page', Math.max(1, filters.page - 1))}
                disabled={filters.page <= 1}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <div className="flex items-center space-x-2">
                {Array.from({ length: Math.min(5, feedbackData.pages) }, (_, i) => {
                  const page = i + 1
                  return (
                    <button
                      key={page}
                      onClick={() => handleFilterChange('page', page)}
                      className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                        page === filters.page
                          ? 'bg-primary-600 text-white'
                          : 'text-neutral-600 hover:bg-neutral-100'
                      }`}
                    >
                      {page}
                    </button>
                  )
                })}
              </div>
              <button
                onClick={() => handleFilterChange('page', Math.min(feedbackData.pages, filters.page + 1))}
                disabled={filters.page >= feedbackData.pages}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FeedbackList