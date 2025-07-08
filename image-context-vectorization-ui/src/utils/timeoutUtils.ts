import { AxiosError } from 'axios';

export interface TimeoutConfig {
  DEFAULT: number;
  UPLOAD: number;
  SEARCH: number;
  PROCESSING: number;
  MODEL_PRELOAD: number;
  HEALTH: number;
}

export const TIMEOUTS: TimeoutConfig = {
  DEFAULT: parseInt(process.env.REACT_APP_API_TIMEOUT || '30000'),
  UPLOAD: parseInt(process.env.REACT_APP_UPLOAD_TIMEOUT || '120000'),
  SEARCH: parseInt(process.env.REACT_APP_SEARCH_TIMEOUT || '60000'),
  PROCESSING: parseInt(process.env.REACT_APP_PROCESSING_TIMEOUT || '300000'),
  MODEL_PRELOAD: parseInt(process.env.REACT_APP_MODEL_PRELOAD_TIMEOUT || '180000'),
  HEALTH: parseInt(process.env.REACT_APP_HEALTH_TIMEOUT || '10000'),
};

export const isTimeoutError = (error: any): boolean => {
  if (error?.code === 'ECONNABORTED') {
    return true;
  }
  
  if (error instanceof AxiosError) {
    return error.code === 'ECONNABORTED' || error.message.includes('timeout');
  }
  
  return error?.message?.toLowerCase().includes('timeout') || false;
};

export const getTimeoutMessage = (operation: keyof TimeoutConfig): string => {
  const timeoutSeconds = TIMEOUTS[operation] / 1000;
  
  const messages = {
    DEFAULT: `Operation timed out after ${timeoutSeconds} seconds`,
    UPLOAD: `File upload timed out after ${timeoutSeconds} seconds. Try uploading smaller files or check your connection.`,
    SEARCH: `Search timed out after ${timeoutSeconds} seconds. The search query might be too complex or the server is busy.`,
    PROCESSING: `Image processing timed out after ${timeoutSeconds} seconds. Large images or server load may cause delays.`,
    MODEL_PRELOAD: `Model preloading timed out after ${timeoutSeconds} seconds. Models may be large or server resources are limited.`,
    HEALTH: `Health check timed out after ${timeoutSeconds} seconds. The API server may be offline or overloaded.`,
  };
  
  return messages[operation];
};

export const formatTimeout = (milliseconds: number): string => {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`;
  } else {
    return `${seconds}s`;
  }
};

export const getRecommendedTimeout = (operation: string, fileSize?: number): number => {
  switch (operation) {
    case 'upload':
      if (fileSize) {
        // Add extra time for larger files (rough estimate: 1MB per 10 seconds)
        const fileMB = fileSize / (1024 * 1024);
        const extraTime = Math.max(0, (fileMB - 1) * 10000); // 10 seconds per MB above 1MB
        return TIMEOUTS.UPLOAD + extraTime;
      }
      return TIMEOUTS.UPLOAD;
    
    case 'processing':
      if (fileSize) {
        // Processing time increases with file size
        const fileMB = fileSize / (1024 * 1024);
        const extraTime = Math.max(0, (fileMB - 5) * 30000); // 30 seconds per MB above 5MB
        return TIMEOUTS.PROCESSING + extraTime;
      }
      return TIMEOUTS.PROCESSING;
    
    default:
      return TIMEOUTS.DEFAULT;
  }
};