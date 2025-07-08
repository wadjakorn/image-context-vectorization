import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ClockIcon, 
  ExclamationTriangleIcon,
  ArrowPathIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import { Task, apiService } from '../services/api';
import toast from 'react-hot-toast';

interface ProcessingStatusProps {
  taskId?: string;
  onTaskComplete?: (task: Task) => void;
  onTaskFailed?: (task: Task) => void;
  refreshInterval?: number;
  className?: string;
}

interface ProcessingStats {
  totalTasks: number;
  activeTasks: number;
  completedTasks: number;
  failedTasks: number;
}

const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  taskId,
  onTaskComplete,
  onTaskFailed,
  refreshInterval = 2000,
  className = '',
}) => {
  const [task, setTask] = useState<Task | null>(null);
  const [allTasks, setAllTasks] = useState<Task[]>([]);
  const [stats, setStats] = useState<ProcessingStats>({
    totalTasks: 0,
    activeTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch specific task status
  const fetchTaskStatus = async (id: string) => {
    try {
      const taskData = await apiService.getTaskStatus(id);
      setTask(taskData);
      
      if (taskData.status === 'completed') {
        onTaskComplete?.(taskData);
        if (autoRefresh) {
          setAutoRefresh(false);
        }
      } else if (taskData.status === 'failed') {
        onTaskFailed?.(taskData);
        if (autoRefresh) {
          setAutoRefresh(false);
        }
      }
    } catch (err) {
      console.error('Failed to fetch task status:', err);
      setError('Failed to fetch task status');
    }
  };

  // Fetch all tasks
  const fetchAllTasks = async () => {
    try {
      const tasksData = await apiService.listTasks();
      setAllTasks(tasksData.tasks || []);
      
      // Calculate stats
      const tasks = tasksData.tasks || [];
      const newStats: ProcessingStats = {
        totalTasks: tasks.length,
        activeTasks: tasks.filter((t: Task) => t.status === 'processing' || t.status === 'queued').length,
        completedTasks: tasks.filter((t: Task) => t.status === 'completed').length,
        failedTasks: tasks.filter((t: Task) => t.status === 'failed').length,
      };
      setStats(newStats);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError('Failed to fetch tasks');
    }
  };

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(async () => {
      if (taskId) {
        await fetchTaskStatus(taskId);
      }
      await fetchAllTasks();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [taskId, autoRefresh, refreshInterval]);

  // Initial load
  useEffect(() => {
    const loadInitialData = async () => {
      setLoading(true);
      try {
        if (taskId) {
          await fetchTaskStatus(taskId);
        }
        await fetchAllTasks();
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [taskId]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'queued':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      case 'processing':
        return <ArrowPathIcon className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <ExclamationTriangleIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'queued':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'processing':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'completed':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'failed':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatDuration = (start: string, end?: string) => {
    const startTime = new Date(start).getTime();
    const endTime = end ? new Date(end).getTime() : Date.now();
    const duration = Math.floor((endTime - startTime) / 1000);
    
    if (duration < 60) {
      return `${duration}s`;
    } else if (duration < 3600) {
      return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    } else {
      return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`;
    }
  };

  const refreshData = async () => {
    setLoading(true);
    try {
      if (taskId) {
        await fetchTaskStatus(taskId);
      }
      await fetchAllTasks();
      toast.success('Data refreshed successfully');
    } catch (err) {
      toast.error('Failed to refresh data');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !task && allTasks.length === 0) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600 dark:text-gray-400">Loading processing status...</span>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Processing Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Tasks</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalTasks}</p>
            </div>
            <DocumentTextIcon className="w-8 h-8 text-gray-400" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active</p>
              <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.activeTasks}</p>
            </div>
            <ArrowPathIcon className="w-8 h-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.completedTasks}</p>
            </div>
            <CheckCircleIcon className="w-8 h-8 text-green-400" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Failed</p>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.failedTasks}</p>
            </div>
            <XCircleIcon className="w-8 h-8 text-red-400" />
          </div>
        </div>
      </div>

      {/* Current Task Status */}
      {task && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Current Task Status
            </h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`px-3 py-1 text-sm rounded-md ${
                  autoRefresh 
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' 
                    : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                }`}
              >
                {autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF'}
              </button>
              <button
                onClick={refreshData}
                disabled={loading}
                className="px-3 py-1 text-sm bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 rounded-md hover:bg-blue-200 dark:hover:bg-blue-900/50 disabled:opacity-50"
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getStatusIcon(task.status)}
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">
                    Task {task.task_id.substring(0, 8)}...
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {task.message}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(task.status)}`}>
                  {task.status.toUpperCase()}
                </span>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  {formatDuration(task.created_at, task.updated_at)}
                </p>
              </div>
            </div>

            {/* Progress Bar */}
            {task.status === 'processing' && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Progress</span>
                  <span className="text-gray-900 dark:text-white">{task.progress.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${task.progress}%` }}
                  ></div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {task.error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-md">
                <div className="flex items-center">
                  <XCircleIcon className="w-5 h-5 text-red-500 mr-2" />
                  <p className="text-sm text-red-700 dark:text-red-300">{task.error}</p>
                </div>
              </div>
            )}

            {/* Result Preview */}
            {task.result && (
              <div className="p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-md">
                <div className="flex items-center mb-2">
                  <CheckCircleIcon className="w-5 h-5 text-green-500 mr-2" />
                  <p className="text-sm font-medium text-green-700 dark:text-green-300">Task Completed</p>
                </div>
                <div className="text-xs text-green-600 dark:text-green-400 font-mono bg-green-100 dark:bg-green-900/50 p-2 rounded">
                  <pre>{JSON.stringify(task.result, null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* All Tasks List */}
      {allTasks.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            All Tasks
          </h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {allTasks.map((taskItem) => (
              <div
                key={taskItem.task_id}
                className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                <div className="flex items-center space-x-3">
                  {getStatusIcon(taskItem.status)}
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {taskItem.task_id.substring(0, 8)}...
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {taskItem.message}
                    </p>
                  </div>
                </div>
                
                <div className="text-right">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(taskItem.status)}`}>
                    {taskItem.status.toUpperCase()}
                  </span>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    {formatDuration(taskItem.created_at, taskItem.updated_at)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center">
            <XCircleIcon className="w-5 h-5 text-red-500 mr-2" />
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessingStatus;