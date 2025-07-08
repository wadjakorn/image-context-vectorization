import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, PhotoIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { apiService, UploadResponse } from '../services/api';
import toast from 'react-hot-toast';

interface ImageUploadProps {
  onUploadComplete?: (response: UploadResponse) => void;
  onUploadStart?: (file: File) => void;
  multiple?: boolean;
  maxFiles?: number;
  maxSize?: number;
  className?: string;
}

interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  response?: UploadResponse;
  error?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  onUploadComplete,
  onUploadStart,
  multiple = false,
  maxFiles = 10,
  maxSize = 10 * 1024 * 1024, // 10MB
  className = '',
}) => {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      const filesToUpload = acceptedFiles.slice(0, maxFiles);
      
      // Initialize upload progress for each file
      const newUploads: UploadProgress[] = filesToUpload.map(file => ({
        file,
        progress: 0,
        status: 'uploading',
      }));

      setUploads(prev => [...prev, ...newUploads]);

      // Upload each file
      for (let i = 0; i < filesToUpload.length; i++) {
        const file = filesToUpload[i];
        onUploadStart?.(file);

        try {
          // Update status to uploading
          setUploads(prev => 
            prev.map(upload => 
              upload.file === file 
                ? { ...upload, status: 'uploading', progress: 50 }
                : upload
            )
          );

          // Upload the file
          const response = await apiService.uploadImage(file, true, false, 'uploads');

          // Update status to processing
          setUploads(prev => 
            prev.map(upload => 
              upload.file === file 
                ? { ...upload, status: 'processing', progress: 80 }
                : upload
            )
          );

          // Simulate processing time
          await new Promise(resolve => setTimeout(resolve, 500));

          // Update status to completed
          setUploads(prev => 
            prev.map(upload => 
              upload.file === file 
                ? { ...upload, status: 'completed', progress: 100, response }
                : upload
            )
          );

          onUploadComplete?.(response);
          toast.success(`Successfully uploaded ${file.name}`);

        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Upload failed';
          
          setUploads(prev => 
            prev.map(upload => 
              upload.file === file 
                ? { ...upload, status: 'error', error: errorMessage }
                : upload
            )
          );

          toast.error(`Failed to upload ${file.name}: ${errorMessage}`);
        }
      }
    },
    [maxFiles, onUploadStart, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive: dropzoneActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    },
    multiple,
    maxFiles,
    maxSize,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
    onDropAccepted: () => setIsDragActive(false),
    onDropRejected: () => setIsDragActive(false),
  });

  const removeUpload = (fileToRemove: File) => {
    setUploads(prev => prev.filter(upload => upload.file !== fileToRemove));
  };

  const clearCompleted = () => {
    setUploads(prev => prev.filter(upload => upload.status !== 'completed'));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
          ${isDragActive || dropzoneActive
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 hover:border-gray-400 dark:border-gray-600 dark:hover:border-gray-500'
          }
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center space-y-3">
          <CloudArrowUpIcon className="w-12 h-12 text-gray-400" />
          
          {isDragActive || dropzoneActive ? (
            <p className="text-lg font-medium text-blue-600 dark:text-blue-400">
              Drop your images here!
            </p>
          ) : (
            <div className="space-y-2">
              <p className="text-lg font-medium text-gray-600 dark:text-gray-300">
                Drag & drop images here, or click to select
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Supports PNG, JPG, JPEG, GIF, BMP, WebP (max {formatFileSize(maxSize)})
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <div className="mt-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              Upload Progress
            </h3>
            <button
              onClick={clearCompleted}
              className="text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              Clear Completed
            </button>
          </div>

          <div className="space-y-3">
            {uploads.map((upload, index) => (
              <div
                key={`${upload.file.name}-${index}`}
                className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <PhotoIcon className="w-8 h-8 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {upload.file.name}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {formatFileSize(upload.file.size)}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <div className="flex items-center space-x-2">
                      {upload.status === 'uploading' && (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                      )}
                      {upload.status === 'processing' && (
                        <div className="animate-pulse rounded-full h-4 w-4 bg-yellow-500"></div>
                      )}
                      {upload.status === 'completed' && (
                        <div className="rounded-full h-4 w-4 bg-green-500"></div>
                      )}
                      {upload.status === 'error' && (
                        <div className="rounded-full h-4 w-4 bg-red-500"></div>
                      )}
                    </div>

                    <button
                      onClick={() => removeUpload(upload.file)}
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                    >
                      <XMarkIcon className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Progress Bar */}
                {upload.status !== 'error' && (
                  <div className="mt-3">
                    <div className="bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          upload.status === 'completed'
                            ? 'bg-green-500'
                            : upload.status === 'processing'
                            ? 'bg-yellow-500'
                            : 'bg-blue-500'
                        }`}
                        style={{ width: `${upload.progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}

                {/* Status Messages */}
                <div className="mt-2 text-sm">
                  {upload.status === 'uploading' && (
                    <span className="text-blue-600 dark:text-blue-400">Uploading...</span>
                  )}
                  {upload.status === 'processing' && (
                    <span className="text-yellow-600 dark:text-yellow-400">Processing...</span>
                  )}
                  {upload.status === 'completed' && (
                    <span className="text-green-600 dark:text-green-400">
                      Completed! {upload.response?.message}
                    </span>
                  )}
                  {upload.status === 'error' && (
                    <span className="text-red-600 dark:text-red-400">
                      Error: {upload.error}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;