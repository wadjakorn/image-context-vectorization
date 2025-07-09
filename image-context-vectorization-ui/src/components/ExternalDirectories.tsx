import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import apiService, { ExternalDirectory, ProcessingStatus } from '../services/api';

const ExternalDirectories: React.FC = () => {
  const [directories, setDirectories] = useState<ExternalDirectory[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingStatus, setProcessingStatus] = useState<Record<string, ProcessingStatus>>({});
  const [scanResults, setScanResults] = useState<Record<string, { total_files: number; image_files: string[] }>>({});

  useEffect(() => {
    loadExternalDirectories();
    loadProcessingStatus();
    
    // Poll processing status every 5 seconds
    const interval = setInterval(loadProcessingStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadExternalDirectories = async () => {
    try {
      setLoading(true);
      const response = await apiService.getExternalDirectories();
      setDirectories(response.external_directories);
    } catch (error) {
      console.error('Error loading external directories:', error);
      toast.error('Failed to load external directories');
    } finally {
      setLoading(false);
    }
  };

  const loadProcessingStatus = async () => {
    try {
      const response = await apiService.getAllProcessingStatus();
      setProcessingStatus(response.processing_tasks);
    } catch (error) {
      console.error('Error loading processing status:', error);
    }
  };

  const handleScanDirectory = async (directoryId: string) => {
    try {
      const response = await apiService.scanExternalDirectory(directoryId);
      setScanResults(prev => ({
        ...prev,
        [directoryId]: {
          total_files: response.total_files,
          image_files: response.image_files
        }
      }));
      toast.success(`Found ${response.total_files} image files in directory`);
    } catch (error: any) {
      console.error('Error scanning directory:', error);
      toast.error(error.response?.data?.detail || 'Failed to scan directory');
    }
  };

  const handleProcessDirectory = async (directoryId: string) => {
    try {
      const response = await apiService.processExternalDirectory(directoryId);
      toast.success(`Started processing ${response.total_files} images`);
      loadProcessingStatus(); // Refresh status immediately
    } catch (error: any) {
      console.error('Error processing directory:', error);
      toast.error(error.response?.data?.detail || 'Failed to process directory');
    }
  };

  const handleRefreshDirectory = async (directoryId: string) => {
    try {
      const response = await apiService.getExternalDirectory(directoryId);
      setDirectories(prev => prev.map(dir => 
        dir.id === directoryId ? response : dir
      ));
      toast.success('Directory status refreshed');
    } catch (error: any) {
      console.error('Error refreshing directory:', error);
      toast.error('Failed to refresh directory status');
    }
  };

  const getStatusColor = (directory: ExternalDirectory) => {
    if (!directory.exists) return 'text-red-500';
    if (!directory.accessible) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getStatusIcon = (directory: ExternalDirectory) => {
    if (!directory.exists) return '❌';
    if (!directory.accessible) return '⚠️';
    return '✅';
  };

  const getProcessingStatusColor = (status: string) => {
    switch (status) {
      case 'processing': return 'text-blue-500';
      case 'completed': return 'text-green-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (directories.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-500 dark:text-gray-400 text-lg mb-4">No external directories configured</div>
        <div className="text-sm text-gray-400 dark:text-gray-500">
          Configure external directories by setting the EXTERNAL_DIRECTORIES environment variable
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">External Directories</h2>
        <button
          onClick={loadExternalDirectories}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Refresh All
        </button>
      </div>

      <div className="grid gap-6">
        {directories.map(directory => {
          const status = processingStatus[directory.id];
          const scanResult = scanResults[directory.id];
          
          return (
            <div 
              key={directory.id} 
              className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{getStatusIcon(directory)}</span>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">{directory.name}</h3>
                    <span className={`text-sm ${getStatusColor(directory)}`}>
                      {directory.accessible ? 'Accessible' : 'Not Accessible'}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                    <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-gray-900 dark:text-gray-100">{directory.path}</code>
                  </div>
                  
                  {directory.error_message && (
                    <div className="text-sm text-red-600 dark:text-red-400 mb-2">
                      Error: {directory.error_message}
                    </div>
                  )}
                  
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Last checked: {formatDate(directory.last_checked)}
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => handleRefreshDirectory(directory.id)}
                    className="px-3 py-1 bg-gray-500 dark:bg-gray-600 text-white rounded text-sm hover:bg-gray-600 dark:hover:bg-gray-500 transition-colors"
                  >
                    Refresh
                  </button>
                  
                  {directory.accessible && (
                    <>
                      <button
                        onClick={() => handleScanDirectory(directory.id)}
                        className="px-3 py-1 bg-blue-500 dark:bg-blue-600 text-white rounded text-sm hover:bg-blue-600 dark:hover:bg-blue-500 transition-colors"
                      >
                        Scan
                      </button>
                      
                      <button
                        onClick={() => handleProcessDirectory(directory.id)}
                        disabled={status?.status === 'processing'}
                        className="px-3 py-1 bg-green-500 dark:bg-green-600 text-white rounded text-sm hover:bg-green-600 dark:hover:bg-green-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {status?.status === 'processing' ? 'Processing...' : 'Process'}
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* Directory Statistics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {directory.image_count ?? '—'}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Total Images</div>
                </div>
                
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {directory.supported_image_count ?? '—'}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Supported</div>
                </div>
                
                {scanResult && (
                  <>
                    <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/30 rounded">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {scanResult.total_files}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Scanned Files</div>
                    </div>
                    
                    <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/30 rounded">
                      <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                        {scanResult.image_files.length}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">Found Images</div>
                    </div>
                  </>
                )}
              </div>

              {/* Processing Status */}
              {status && (
                <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900 dark:text-white">Processing Status:</span>
                    <span className={`font-semibold ${getProcessingStatusColor(status.status)}`}>
                      {status.status.toUpperCase()}
                    </span>
                  </div>
                  
                  {status.total_files && (
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div className="text-center">
                        <div className="font-bold text-blue-600 dark:text-blue-400">
                          {status.total_files}
                        </div>
                        <div className="text-gray-500 dark:text-gray-400">Total</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="font-bold text-green-600 dark:text-green-400">
                          {status.processed_files || 0}
                        </div>
                        <div className="text-gray-500 dark:text-gray-400">Processed</div>
                      </div>
                      
                      <div className="text-center">
                        <div className="font-bold text-red-600 dark:text-red-400">
                          {status.failed_files || 0}
                        </div>
                        <div className="text-gray-500 dark:text-gray-400">Failed</div>
                      </div>
                    </div>
                  )}
                  
                  {status.status === 'processing' && status.total_files && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-blue-500 dark:bg-blue-400 h-2 rounded-full transition-all duration-500"
                          style={{ 
                            width: `${((status.processed_files || 0) / status.total_files) * 100}%` 
                          }}
                        />
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {Math.round(((status.processed_files || 0) / status.total_files) * 100)}% complete
                      </div>
                    </div>
                  )}
                  
                  {status.error_message && (
                    <div className="mt-2 text-sm text-red-600 dark:text-red-400">
                      Error: {status.error_message}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ExternalDirectories;