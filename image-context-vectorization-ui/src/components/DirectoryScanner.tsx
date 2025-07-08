import React, { useState } from 'react';
import { FolderIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { apiService } from '../services/api';

interface ScanResult {
  total_files: number;
  already_processed: number;
  new_files: number;
  new_file_paths: string[];
}

interface ProcessingTask {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'queued';
  progress?: number;
  total_files?: number;
  processed_files?: number;
  result?: any;
}

const DirectoryScanner: React.FC = () => {
  const [scanning, setScanning] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [reprocessing, setReprocessing] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [processingTask, setProcessingTask] = useState<ProcessingTask | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScanDirectory = async () => {
    setScanning(true);
    setError(null);
    setScanResult(null);
    
    try {
      const result = await apiService.scanDirectory('uploads');
      setScanResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to scan directory');
    } finally {
      setScanning(false);
    }
  };

  const handleProcessImages = async () => {
    if (!scanResult || scanResult.new_files === 0) return;
    
    setProcessing(true);
    setError(null);
    
    try {
      const response = await apiService.processDirectoryAsync('uploads');
      const task: ProcessingTask = {
        task_id: response.task_id,
        status: 'pending'
      };
      setProcessingTask(task);
      pollTaskStatus(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start processing');
      setProcessing(false);
    }
  };

  const pollTaskStatus = async (taskId: string) => {
    const poll = async () => {
      try {
        const status = await apiService.getTaskStatus(taskId);
        setProcessingTask(status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          setProcessing(false);
          setReprocessing(false);
          if (status.status === 'completed') {
            setScanResult(null); // Clear scan result after successful processing
          }
        } else {
          setTimeout(poll, 3000); // Poll every 3 seconds
        }
      } catch (err) {
        setError('Failed to get task status');
        setProcessing(false);
        setReprocessing(false);
      }
    };
    
    poll();
  };

  const handleReprocessAll = async () => {
    if (!window.confirm('This will clear all images from the database and reprocess everything. Are you sure?')) {
      return;
    }

    setReprocessing(true);
    setError(null);
    setScanResult(null);
    setProcessingTask(null);

    try {
      // Clear database
      await apiService.clearAllImages();
      
      // Process all images with force reprocess
      const response = await apiService.processDirectoryAsync('uploads');
      const task: ProcessingTask = {
        task_id: response.task_id,
        status: 'pending'
      };
      setProcessingTask(task);
      pollTaskStatus(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start reprocessing');
      setReprocessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center gap-2 mb-4">
          <FolderIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Directory Scanner
          </h3>
        </div>
        
        <div className="space-y-4">
          <div className="flex gap-2 flex-wrap">
            <button 
              onClick={handleScanDirectory}
              disabled={scanning || processing || reprocessing}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {scanning ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Scanning...
                </>
              ) : (
                'Scan Images'
              )}
            </button>
            
            {scanResult && scanResult.new_files > 0 && (
              <button 
                onClick={handleProcessImages}
                disabled={processing || reprocessing}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Processing...
                  </>
                ) : (
                  `Process ${scanResult.new_files} New Images`
                )}
              </button>
            )}
            
            <button 
              onClick={handleReprocessAll}
              disabled={scanning || processing || reprocessing}
              className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {reprocessing ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Re-processing...
                </>
              ) : (
                'Re-Process All Images'
              )}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <ExclamationTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-400" />
                <span className="text-red-800 dark:text-red-200">{error}</span>
              </div>
            </div>
          )}

          {scanResult && (
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5 text-green-600 dark:text-green-400" />
                <span className="text-green-800 dark:text-green-200">
                  Found {scanResult.total_files} total files in uploads directory.
                  {scanResult.new_files > 0 ? (
                    <> {scanResult.new_files} new images ready to process.</>
                  ) : (
                    <> All images already processed.</>
                  )}
                </span>
              </div>
            </div>
          )}

          {processingTask && (
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5 text-blue-600 dark:text-blue-400" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span className="text-blue-800 dark:text-blue-200">
                  Processing Status: {processingTask.status}
                  {processingTask.processed_files !== undefined && processingTask.total_files && (
                    <> ({processingTask.processed_files}/{processingTask.total_files})</>
                  )}
                  <br />
                  <span className="text-sm opacity-75">Checking status every 3 seconds...</span>
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DirectoryScanner;