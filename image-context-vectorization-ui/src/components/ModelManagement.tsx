import React, { useState, useEffect } from 'react';
import { 
  CpuChipIcon, 
  PlayIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ClockIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { apiService, ModelStatus, ModelPreloadResponse } from '../services/api';
import TimeoutIndicator from './TimeoutIndicator';
import toast from 'react-hot-toast';

interface ModelManagementProps {
  className?: string;
}

const ModelManagement: React.FC<ModelManagementProps> = ({ className = '' }) => {
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [preloadData, setPreloadData] = useState<ModelPreloadResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [preloading, setPreloading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Load model status
  const loadModelStatus = async () => {
    try {
      const status = await apiService.getModelStatus();
      setModelStatus(status);
    } catch (error) {
      console.error('Failed to load model status:', error);
      toast.error('Failed to load model status');
    }
  };

  // Preload all models
  const handlePreloadModels = async () => {
    setPreloading(true);
    try {
      const response = await apiService.preloadModels();
      setPreloadData(response);
      await loadModelStatus(); // Refresh status after preloading
      toast.success(`Models preloaded successfully in ${response.timings.total.toFixed(2)}s`);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to preload models';
      toast.error(errorMessage);
    } finally {
      setPreloading(false);
    }
  };

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(loadModelStatus, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [autoRefresh]);

  // Initial load
  useEffect(() => {
    loadModelStatus();
  }, []);

  const refreshData = async () => {
    setLoading(true);
    try {
      await loadModelStatus();
      toast.success('Model status refreshed');
    } catch (error) {
      toast.error('Failed to refresh model status');
    } finally {
      setLoading(false);
    }
  };

  const getModelIcon = (isLoaded: boolean) => {
    return isLoaded ? (
      <CheckCircleIcon className="w-5 h-5 text-green-500" />
    ) : (
      <XCircleIcon className="w-5 h-5 text-gray-400" />
    );
  };

  const formatModelName = (modelKey: string) => {
    const names: { [key: string]: string } = {
      sentence_transformer: 'Sentence Transformer',
      blip_processor: 'BLIP Processor',
      blip_model: 'BLIP Model',
      clip_processor: 'CLIP Processor',
      clip_model: 'CLIP Model'
    };
    return names[modelKey] || modelKey;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getLoadedModelsCount = () => {
    if (!modelStatus?.model_info) return 0;
    const { blip, clip, sentence_transformer } = modelStatus.model_info;
    return [blip?.loaded, clip?.loaded, sentence_transformer?.loaded].filter(Boolean).length;
  };

  const getTotalModelsCount = () => {
    return 2; // BLIP, CLIP
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Model Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Models Loaded</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {getLoadedModelsCount()}/{getTotalModelsCount()}
              </p>
            </div>
            <CpuChipIcon className="w-8 h-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Device</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white uppercase">
                {modelStatus?.device || 'Unknown'}
              </p>
            </div>
            <CpuChipIcon className="w-8 h-8 text-purple-400" />
          </div>
        </div>

      </div>

      {/* Model Details */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Model Status
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

        {modelStatus ? (
          <div className="space-y-3">
            {/* BLIP Model */}
            {modelStatus.model_info?.blip && (
              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                <div className="flex items-center space-x-3">
                  {getModelIcon(modelStatus.model_info.blip.loaded)}
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      BLIP Model
                    </p>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {modelStatus.model_info.blip.name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {modelStatus.model_info.blip.source}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* CLIP Model */}
            {modelStatus.model_info?.clip && (
              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                <div className="flex items-center space-x-3">
                  {getModelIcon(modelStatus.model_info.clip.loaded)}
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      CLIP Model
                    </p>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {modelStatus.model_info.clip.name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {modelStatus.model_info.clip.source}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Sentence Transformer */}
            {modelStatus.model_info?.sentence_transformer && (
              <div className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-md">
                <div className="flex items-center space-x-3">
                  {getModelIcon(modelStatus.model_info.sentence_transformer.loaded)}
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      Sentence Transformer
                    </p>
                    <p className="text-sm text-gray-900 dark:text-white">
                      {modelStatus.model_info.sentence_transformer.name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {modelStatus.model_info.sentence_transformer.source}
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Last updated: {formatTimestamp(modelStatus.timestamp)}
              </p>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading model status...</p>
          </div>
        )}
      </div>

      {/* Preload Models Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Model Preloading
        </h3>
        
        <div className="space-y-4">
          <p className="text-gray-600 dark:text-gray-400">
            Preload all models into memory for faster processing.
          </p>
          
          <button
            onClick={handlePreloadModels}
            disabled={preloading}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {preloading ? (
              <ArrowPathIcon className="w-4 h-4 animate-spin" />
            ) : (
              <PlayIcon className="w-4 h-4" />
            )}
            <span>{preloading ? 'Preloading...' : 'Preload All Models'}</span>
          </button>

          {preloadData && (
            <div className="p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-md">
              <div className="flex items-center">
                <CheckCircleIcon className="w-5 h-5 text-green-500 mr-2" />
                <p className="text-sm font-medium text-green-700 dark:text-green-300">
                  Models preloaded successfully!
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ModelManagement;