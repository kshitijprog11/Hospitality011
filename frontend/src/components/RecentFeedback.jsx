import React from 'react'
import { formatDistanceToNow } from 'date-fns'
import { 
  FaceSmileIcon, 
  FaceFrownIcon, 
  FaceIcon as FaceNeutralIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

const RecentFeedback = ({ feedback = [] }) => {
  if (!feedback || feedback.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-neutral-400 mb-2">
          <svg className="w-12 h-12 mx-auto" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <p className="text-neutral-500">No recent feedback available</p>
        <p className="text-sm text-neutral-400">New feedback will appear here</p>
      </div>
    )
  }

  const getSentimentIcon = (sentimentLabel, sentiment) => {
    switch (sentimentLabel) {
      case 'positive':
        return <FaceSmileIcon className="h-5 w-5 text-success-500" />
      case 'negative':
        return <FaceFrownIcon className="h-5 w-5 text-danger-500" />
      default:
        return <FaceNeutralIcon className="h-5 w-5 text-neutral-500" />
    }
  }

  const getSentimentBadge = (sentimentLabel, sentiment) => {
    const baseClasses = 'text-xs px-2 py-0.5 rounded-full font-medium'
    
    switch (sentimentLabel) {
      case 'positive':
        return `${baseClasses} bg-success-100 text-success-700`
      case 'negative':
        return `${baseClasses} bg-danger-100 text-danger-700`
      default:
        return `${baseClasses} bg-neutral-100 text-neutral-700`
    }
  }

  const getChannelBadge = (channel) => {
    const baseClasses = 'text-xs px-2 py-0.5 rounded-full font-medium'
    
    switch (channel) {
      case 'web':
        return `${baseClasses} bg-blue-100 text-blue-700`
      case 'email':
        return `${baseClasses} bg-purple-100 text-purple-700`
      case 'whatsapp':
        return `${baseClasses} bg-green-100 text-green-700`
      case 'google_reviews':
        return `${baseClasses} bg-red-100 text-red-700`
      default:
        return `${baseClasses} bg-neutral-100 text-neutral-700`
    }
  }

  return (
    <div className="space-y-4">
      {feedback.map((item, index) => (
        <div
          key={item.id || index}
          className={clsx(
            'p-4 rounded-xl border transition-all duration-200 hover:shadow-md',
            item.flagged 
              ? 'bg-danger-50 border-danger-200' 
              : 'bg-white border-neutral-200'
          )}
        >
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-2">
              {getSentimentIcon(item.sentiment_label, item.sentiment)}
              {item.guest_name && (
                <span className="text-sm font-medium text-neutral-900">
                  {item.guest_name}
                </span>
              )}
              {item.flagged && (
                <ExclamationTriangleIcon className="h-4 w-4 text-danger-500" />
              )}
            </div>
            <div className="flex items-center space-x-2">
              <span className={getSentimentBadge(item.sentiment_label, item.sentiment)}>
                {item.sentiment_label}
                {item.sentiment && ` (${item.sentiment.toFixed(2)})`}
              </span>
            </div>
          </div>

          {/* Feedback text */}
          <p className="text-sm text-neutral-700 line-clamp-3 mb-3">
            {item.text}
          </p>

          {/* Topics */}
          {item.topics && item.topics.length > 0 && (
            <div className="flex flex-wrap gap-1 mb-3">
              {item.topics.slice(0, 3).map((topic, topicIndex) => (
                <span
                  key={topicIndex}
                  className="text-xs px-2 py-0.5 bg-primary-50 text-primary-700 rounded-full"
                >
                  {topic}
                </span>
              ))}
              {item.topics.length > 3 && (
                <span className="text-xs px-2 py-0.5 bg-neutral-100 text-neutral-600 rounded-full">
                  +{item.topics.length - 3} more
                </span>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="flex items-center justify-between text-xs text-neutral-500">
            <div className="flex items-center space-x-3">
              <span className={getChannelBadge(item.channel)}>
                {item.channel.replace('_', ' ')}
              </span>
              {item.location && (
                <span>📍 {item.location}</span>
              )}
              {item.booking_reference && (
                <span>🎫 {item.booking_reference}</span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              {item.priority && item.priority !== 'normal' && (
                <span className={clsx(
                  'text-xs px-2 py-0.5 rounded-full font-medium',
                  item.priority === 'urgent' ? 'bg-danger-100 text-danger-700' :
                  item.priority === 'high' ? 'bg-warning-100 text-warning-700' :
                  'bg-neutral-100 text-neutral-700'
                )}>
                  {item.priority}
                </span>
              )}
              <span>
                {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
              </span>
            </div>
          </div>
        </div>
      ))}

      {/* View all link */}
      {feedback.length > 0 && (
        <div className="text-center pt-2">
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            View all feedback →
          </button>
        </div>
      )}
    </div>
  )
}

export default RecentFeedback