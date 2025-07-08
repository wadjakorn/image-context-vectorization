import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { 
  PhotoIcon, 
  MagnifyingGlassIcon, 
  FolderIcon,
  CogIcon,
  CpuChipIcon,
  HeartIcon
} from '@heroicons/react/24/outline';
import ImageUpload from './components/ImageUpload';
import ImageBrowser from './components/ImageBrowser';
import ProcessingStatus from './components/ProcessingStatus';
import ModelManagement from './components/ModelManagement';
import DirectoryScanner from './components/DirectoryScanner';
import { apiService, HealthResponse } from './services/api';
import toast from 'react-hot-toast';

type TabType = 'upload' | 'browse' | 'processing' | 'models' | 'directory';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('upload');
  const [health, setHealth] = useState<HealthResponse | null>(null);

  // Load health status on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const healthResponse = await apiService.getHealth();
        setHealth(healthResponse);
      } catch (error) {
        console.error('Failed to load health status:', error);
        // Set a default health object to prevent null reference errors
        setHealth({
          status: 'unhealthy',
          version: 'unknown',
          database_connected: false,
          models_loaded: false,
          uptime: 0,
          stats: {
            total_images: 0,
            collection_name: 'unknown',
            db_path: 'unknown'
          }
        });
        toast.error('Failed to connect to API server');
      }
    };

    loadInitialData();
  }, []);

  // Tab configuration
  const tabs = [
    { id: 'upload' as TabType, name: 'Upload', icon: PhotoIcon },
    { id: 'browse' as TabType, name: 'Browse & Search', icon: MagnifyingGlassIcon },
    { id: 'processing' as TabType, name: 'Processing', icon: CogIcon },
    { id: 'models' as TabType, name: 'Models', icon: CpuChipIcon },
    { id: 'directory' as TabType, name: 'Directory', icon: FolderIcon },
  ];

  const handleUploadComplete = () => {
    toast.success('Upload completed successfully!');
    // Switch to browse tab to see uploaded images
    setActiveTab('browse');
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'upload':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Upload Images
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Upload images to extract context and enable AI-powered search
              </p>
            </div>
            <ImageUpload
              onUploadComplete={handleUploadComplete}
              multiple={true}
              maxFiles={10}
              className="max-w-2xl mx-auto"
            />
          </div>
        );

      case 'browse':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Browse & Search Images
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Browse all images or search using natural language descriptions
              </p>
            </div>
            <ImageBrowser />
          </div>
        );

      case 'processing':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Processing Status
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Monitor image processing tasks and system status
              </p>
            </div>
            <ProcessingStatus />
          </div>
        );

      case 'models':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Model Management
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Monitor AI model loading status and preload models for faster processing
              </p>
            </div>
            <ModelManagement />
          </div>
        );

      case 'directory':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Directory Processing
              </h2>
              <p className="text-gray-600 dark:text-gray-400">
                Scan and process images from the uploads directory
              </p>
            </div>
            <div className="max-w-2xl mx-auto">
              <DirectoryScanner />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <PhotoIcon className="w-8 h-8 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                Image Context Vectorization
              </h1>
            </div>
            
            {/* Status Indicator */}
            <div className="flex items-center space-x-4">
              {health && (
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    health.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {health.status === 'healthy' && health.database_connected 
                      ? 'Connected' 
                      : health.status === 'unhealthy' 
                      ? 'API Offline' 
                      : 'DB Disconnected'
                    }
                  </span>
                </div>
              )}
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {health?.stats?.total_images || 0} images
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-200'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderTabContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
            <span>Made with</span>
            <HeartIcon className="w-4 h-4 text-red-500" />
            <span>for AI-powered image management</span>
          </div>
        </div>
      </footer>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </div>
  );
}

export default App;
