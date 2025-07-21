import React from 'react'
import clsx from 'clsx'

const TopicsCloud = ({ topics = [] }) => {
  if (!topics || topics.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <p className="text-neutral-500">No topics data available</p>
      </div>
    )
  }

  // Get the max count for sizing
  const maxCount = Math.max(...topics.map(topic => topic.count), 1)
  
  // Function to get size class based on count
  const getSizeClass = (count) => {
    const ratio = count / maxCount
    if (ratio > 0.8) return 'text-lg font-bold'
    if (ratio > 0.6) return 'text-base font-semibold'
    if (ratio > 0.4) return 'text-sm font-medium'
    return 'text-xs font-normal'
  }

  // Function to get color based on sentiment
  const getSentimentColor = (sentiment) => {
    if (sentiment > 0.2) return 'text-success-600 bg-success-50 border-success-200'
    if (sentiment < -0.2) return 'text-danger-600 bg-danger-50 border-danger-200'
    return 'text-neutral-600 bg-neutral-50 border-neutral-200'
  }

  return (
    <div className="space-y-4">
      {/* Topic cloud */}
      <div className="flex flex-wrap gap-2">
        {topics.slice(0, 12).map((topic, index) => (
          <div
            key={index}
            className={clsx(
              'px-3 py-1.5 rounded-full border transition-all duration-200 hover:shadow-sm cursor-pointer',
              getSizeClass(topic.count),
              getSentimentColor(topic.sentiment_avg)
            )}
            title={`${topic.topic}: ${topic.count} mentions, avg sentiment: ${topic.sentiment_avg.toFixed(2)}`}
          >
            <span className="capitalize">{topic.topic}</span>
            <span className="ml-1 text-xs opacity-75">({topic.count})</span>
          </div>
        ))}
      </div>

      {/* Topic list with details */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-neutral-700 mb-3">Top Discussed Topics</h4>
        {topics.slice(0, 5).map((topic, index) => (
          <div key={index} className="flex items-center justify-between py-2">
            <div className="flex items-center space-x-3">
              <div className={clsx(
                'w-2 h-2 rounded-full',
                topic.sentiment_avg > 0.2 ? 'bg-success-400' :
                topic.sentiment_avg < -0.2 ? 'bg-danger-400' : 'bg-neutral-400'
              )} />
              <span className="text-sm font-medium text-neutral-900 capitalize">
                {topic.topic}
              </span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-xs text-neutral-500">
                {topic.count} mentions
              </span>
              <div className={clsx(
                'text-xs px-2 py-0.5 rounded-full',
                topic.sentiment_avg > 0.2 ? 'bg-success-100 text-success-700' :
                topic.sentiment_avg < -0.2 ? 'bg-danger-100 text-danger-700' :
                'bg-neutral-100 text-neutral-700'
              )}>
                {topic.sentiment_avg > 0 ? '+' : ''}{topic.sentiment_avg.toFixed(2)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="pt-3 border-t border-neutral-200">
        <div className="flex items-center justify-between text-xs text-neutral-500">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-success-400" />
              <span>Positive</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-neutral-400" />
              <span>Neutral</span>
            </div>
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full bg-danger-400" />
              <span>Negative</span>
            </div>
          </div>
          <span>Size = frequency</span>
        </div>
      </div>
    </div>
  )
}

export default TopicsCloud