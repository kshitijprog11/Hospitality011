import React from 'react'
import { useQuery } from 'react-query'
import { motion } from 'framer-motion'
import {
  ChatBubbleLeftRightIcon,
  ExclamationTriangleIcon,
  FaceSmileIcon,
  FaceFrownIcon,
  ChartBarIcon,
  TrendingUpIcon,
  TrendingDownIcon,
} from '@heroicons/react/24/outline'

import { feedbackAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import SentimentChart from '../components/SentimentChart'
import TopicsCloud from '../components/TopicsCloud'
import RecentFeedback from '../components/RecentFeedback'

function Dashboard() {
  // Fetch analytics data
  const { data: analytics, isLoading: analyticsLoading, error: analyticsError } = useQuery(
    'dashboard-analytics',
    () => feedbackAPI.getAnalytics(),
    {
      select: (response) => response.data,
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  )

  // Fetch recent feedback
  const { data: recentFeedback, isLoading: feedbackLoading } = useQuery(
    'recent-feedback',
    () => feedbackAPI.getList({ page: 1, size: 5 }),
    {
      select: (response) => response.data,
      refetchInterval: 30000,
    }
  )

  // Fetch flagged feedback for alerts
  const { data: flaggedFeedback } = useQuery(
    'flagged-feedback',
    () => feedbackAPI.getFlagged(5),
    {
      select: (response) => response.data,
      refetchInterval: 15000, // More frequent for alerts
    }
  )

  if (analyticsLoading || feedbackLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  if (analyticsError) {
    return <ErrorMessage message="Failed to load dashboard data" />
  }

  // Calculate metrics
  const totalFeedback = analytics?.total_feedback || 0
  const flaggedCount = analytics?.flagged_count || 0
  const averageSentiment = analytics?.average_sentiment || 0
  const positiveCount = analytics?.sentiment_distribution?.positive || 0
  const negativeCount = analytics?.sentiment_distribution?.negative || 0
  const neutralCount = analytics?.sentiment_distribution?.neutral || 0

  // Calculate sentiment percentages
  const positivePercentage = totalFeedback > 0 ? (positiveCount / totalFeedback) * 100 : 0
  const negativePercentage = totalFeedback > 0 ? (negativeCount / totalFeedback) * 100 : 0

  const metrics = [
    {
      name: 'Total Feedback',
      value: totalFeedback.toLocaleString(),
      icon: ChatBubbleLeftRightIcon,
      color: 'primary',
      trend: '+12%',
      trendDirection: 'up',
    },
    {
      name: 'Flagged Issues',
      value: flaggedCount,
      icon: ExclamationTriangleIcon,
      color: 'danger',
      trend: '-5%',
      trendDirection: 'down',
    },
    {
      name: 'Positive Sentiment',
      value: `${positivePercentage.toFixed(1)}%`,
      icon: FaceSmileIcon,
      color: 'success',
      trend: '+3%',
      trendDirection: 'up',
    },
    {
      name: 'Average Sentiment',
      value: averageSentiment.toFixed(2),
      icon: ChartBarIcon,
      color: averageSentiment > 0 ? 'success' : averageSentiment < 0 ? 'danger' : 'neutral',
      trend: `${averageSentiment > 0 ? '+' : ''}${(averageSentiment * 100).toFixed(1)}%`,
      trendDirection: averageSentiment > 0 ? 'up' : 'down',
    },
  ]

  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    success: 'bg-success-50 text-success-600',
    danger: 'bg-danger-50 text-danger-600',
    warning: 'bg-warning-50 text-warning-600',
    neutral: 'bg-neutral-50 text-neutral-600',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-neutral-900">Dashboard Overview</h2>
        <p className="text-neutral-600 mt-1">
          Monitor your guest feedback and sentiment in real-time
        </p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-2xl p-6 shadow-soft border border-neutral-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-neutral-600">{metric.name}</p>
                <p className="text-2xl font-bold text-neutral-900 mt-1">{metric.value}</p>
                <div className="flex items-center mt-2">
                  {metric.trendDirection === 'up' ? (
                    <TrendingUpIcon className="h-4 w-4 text-success-500 mr-1" />
                  ) : (
                    <TrendingDownIcon className="h-4 w-4 text-danger-500 mr-1" />
                  )}
                  <span className={clsx(
                    'text-xs font-medium',
                    metric.trendDirection === 'up' ? 'text-success-600' : 'text-danger-600'
                  )}>
                    {metric.trend}
                  </span>
                  <span className="text-xs text-neutral-500 ml-1">vs last month</span>
                </div>
              </div>
              <div className={clsx('p-3 rounded-xl', colorClasses[metric.color])}>
                <metric.icon className="h-6 w-6" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl p-6 shadow-soft border border-neutral-200"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-neutral-900">Sentiment Distribution</h3>
            <div className="flex space-x-2">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-success-400 mr-2" />
                <span className="text-sm text-neutral-600">Positive</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-neutral-300 mr-2" />
                <span className="text-sm text-neutral-600">Neutral</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-danger-400 mr-2" />
                <span className="text-sm text-neutral-600">Negative</span>
              </div>
            </div>
          </div>
          <SentimentChart data={analytics?.sentiment_distribution} />
        </motion.div>

        {/* Top Topics */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-2xl p-6 shadow-soft border border-neutral-200"
        >
          <h3 className="text-lg font-semibold text-neutral-900 mb-6">Top Discussion Topics</h3>
          <TopicsCloud topics={analytics?.top_topics} />
        </motion.div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Feedback */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl p-6 shadow-soft border border-neutral-200"
        >
          <h3 className="text-lg font-semibold text-neutral-900 mb-6">Recent Feedback</h3>
          <RecentFeedback feedback={recentFeedback?.items || []} />
        </motion.div>

        {/* Urgent Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-white rounded-2xl p-6 shadow-soft border border-neutral-200"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-neutral-900">Urgent Alerts</h3>
            {flaggedFeedback?.length > 0 && (
              <span className="bg-danger-100 text-danger-800 text-xs px-2 py-1 rounded-full">
                {flaggedFeedback.length} pending
              </span>
            )}
          </div>
          
          {flaggedFeedback?.length > 0 ? (
            <div className="space-y-3">
              {flaggedFeedback.slice(0, 3).map((feedback) => (
                <div key={feedback.id} className="p-3 bg-danger-50 rounded-lg border border-danger-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm text-neutral-900 line-clamp-2">
                        {feedback.text}
                      </p>
                      <div className="flex items-center mt-2 space-x-2">
                        <span className="text-xs text-neutral-500">
                          {feedback.channel} • {feedback.location}
                        </span>
                        <span className={clsx(
                          'text-xs px-2 py-0.5 rounded-full',
                          feedback.priority === 'urgent' ? 'bg-danger-100 text-danger-700' :
                          feedback.priority === 'high' ? 'bg-warning-100 text-warning-700' :
                          'bg-neutral-100 text-neutral-700'
                        )}>
                          {feedback.priority}
                        </span>
                      </div>
                    </div>
                    <ExclamationTriangleIcon className="h-5 w-5 text-danger-500 ml-3 flex-shrink-0" />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FaceSmileIcon className="h-12 w-12 text-success-300 mx-auto mb-3" />
              <p className="text-neutral-500">No urgent alerts at the moment</p>
              <p className="text-sm text-neutral-400">Great job staying on top of issues!</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default Dashboard