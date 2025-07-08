import React, { useState, useEffect } from 'react';
import { ClockIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface TimeoutIndicatorProps {
  isLoading: boolean;
  operation: 'upload' | 'search' | 'processing' | 'preload' | 'health' | 'default';
  onTimeout?: () => void;
  className?: string;
}

const TimeoutIndicator: React.FC<TimeoutIndicatorProps> = ({
  isLoading,
  operation,
  onTimeout,
  className = '',
}) => {
  const [elapsed, setElapsed] = useState(0);
  const [showWarning, setShowWarning] = useState(false);

  // Timeout configurations (in seconds)
  const timeouts = {
    upload: 120,      // 2 minutes
    search: 60,       // 1 minute
    processing: 300,  // 5 minutes
    preload: 180,     // 3 minutes
    health: 10,       // 10 seconds
    default: 30,      // 30 seconds
  };

  const timeout = timeouts[operation];
  const warningThreshold = Math.floor(timeout * 0.75); // Show warning at 75% of timeout

  useEffect(() => {
    if (!isLoading) {
      setElapsed(0);
      setShowWarning(false);
      return;
    }

    const interval = setInterval(() => {
      setElapsed(prev => {
        const newElapsed = prev + 1;
        
        // Show warning when approaching timeout
        if (newElapsed >= warningThreshold && !showWarning) {
          setShowWarning(true);
        }
        
        // Call timeout callback when exceeded
        if (newElapsed >= timeout && onTimeout) {
          onTimeout();
        }
        
        return newElapsed;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isLoading, timeout, warningThreshold, showWarning, onTimeout]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const getProgressPercentage = () => {
    return Math.min((elapsed / timeout) * 100, 100);
  };

  const getOperationLabel = () => {
    const labels = {
      upload: 'File Upload',
      search: 'Image Search',
      processing: 'Image Processing',
      preload: 'Model Preloading',
      health: 'Health Check',
      default: 'Operation',
    };
    return labels[operation];
  };

  if (!isLoading) {
    return null;
  }

  return (
    <div className={`bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <ClockIcon className="w-4 h-4 text-gray-500" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {getOperationLabel()} in progress...
          </span>
        </div>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {formatTime(elapsed)} / {formatTime(timeout)}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
        <div
          className={`h-2 rounded-full transition-all duration-1000 ${
            showWarning ? 'bg-yellow-500' : 'bg-blue-500'
          }`}
          style={{ width: `${getProgressPercentage()}%` }}
        ></div>
      </div>

      {/* Warning Message */}
      {showWarning && (
        <div className="flex items-center space-x-2 text-yellow-600 dark:text-yellow-400">
          <ExclamationTriangleIcon className="w-4 h-4" />
          <span className="text-xs">
            Operation is taking longer than expected. This may indicate a slow connection or server load.
          </span>
        </div>
      )}

      {/* Timeout Message */}
      {elapsed >= timeout && (
        <div className="flex items-center space-x-2 text-red-600 dark:text-red-400 mt-2">
          <ExclamationTriangleIcon className="w-4 h-4" />
          <span className="text-xs">
            Operation has exceeded the expected timeout. Please check your connection or try again.
          </span>
        </div>
      )}

      {/* Expected Duration Info */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
        Expected duration: up to {formatTime(timeout)}
      </div>
    </div>
  );
};

export default TimeoutIndicator;