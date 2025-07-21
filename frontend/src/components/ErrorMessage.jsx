import React from 'react'
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'

const ErrorMessage = ({ 
  message = 'An error occurred', 
  className = '',
  showIcon = true,
  ...props 
}) => {
  return (
    <div 
      className={clsx(
        'bg-danger-50 border border-danger-200 rounded-xl p-4',
        'flex items-center space-x-3',
        className
      )}
      {...props}
    >
      {showIcon && (
        <ExclamationTriangleIcon className="h-5 w-5 text-danger-500 flex-shrink-0" />
      )}
      <div className="flex-1">
        <p className="text-sm font-medium text-danger-800">
          {message}
        </p>
      </div>
    </div>
  )
}

export default ErrorMessage