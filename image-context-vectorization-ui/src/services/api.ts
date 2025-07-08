import axios from 'axios';
import { TIMEOUTS } from '../utils/timeoutUtils';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: TIMEOUTS.DEFAULT,
  headers: {
    'Content-Type': 'application/json',
  },
});


export interface ImageInfo {
  id: string;
  path: string;
  filename: string;
  size: [number, number];
  file_size: number;
  format: string;
  caption: string;
  objects: string[];
}

export interface ProcessImageResponse {
  success: boolean;
  image_id: string;
  message: string;
  image_info: ImageInfo;
  processing_time: number;
  was_duplicate: boolean;
}

export interface SearchResult {
  id: string;
  image_path: string;
  caption: string;
  objects: string[];
  distance: number;
  score: number;
  metadata?: any;
}

export interface SearchResponse {
  success: boolean;
  query: string;
  total_results: number;
  results: SearchResult[];
  search_time: number;
  message: string;
}

export interface UploadResponse {
  success: boolean;
  filename: string;
  file_path: string;
  file_size: number;
  image_id?: string;
  message: string;
}

export interface DirectoryProcessResponse {
  success: boolean;
  total_files: number;
  processed: number;
  skipped: number;
  failed: number;
  processed_ids: string[];
  failed_files: string[];
  processing_time: number;
  message: string;
}

export interface Task {
  task_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  result?: any;
  error?: string;
  created_at: string;
  updated_at: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  database_connected: boolean;
  models_loaded: boolean;
  uptime: number;
  stats: {
    total_images: number;
    collection_name: string;
    db_path: string;
  };
}

export interface ModelInfo {
  name: string;
  source: string;
  loaded: boolean;
}

export interface ModelStatus {
  models: {
    blip_processor: boolean;
    blip_model: boolean;
    clip_processor: boolean;
    clip_model: boolean;
    sentence_transformer: boolean;
  };
  model_info: {
    blip: ModelInfo;
    clip: ModelInfo;
    sentence_transformer: ModelInfo;
    device: string;
  };
  device: string;
  timestamp: string;
}

export interface ModelPreloadResponse {
  success: boolean;
  timings: {
    sentence_transformer: number;
    blip_processor: number;
    blip_model: number;
    clip_processor: number;
    clip_model: number;
    total: number;
  };
  device: string;
  timestamp: string;
}

export const apiService = {
  // Health & Status
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get('/api/v1/health', {
      timeout: TIMEOUTS.HEALTH,
    });
    return response.data;
  },

  async getStatus() {
    const response = await api.get('/api/v1/status');
    return response.data;
  },

  async getConfig() {
    const response = await api.get('/api/v1/config');
    return response.data;
  },

  async getMetrics() {
    const response = await api.get('/api/v1/metrics');
    return response.data;
  },

  // Model Management
  async getModelStatus(): Promise<ModelStatus> {
    const response = await api.get('/api/v1/models/status');
    return response.data;
  },

  async preloadModels(): Promise<ModelPreloadResponse> {
    const response = await api.post('/api/v1/models/preload', {}, {
      timeout: TIMEOUTS.MODEL_PRELOAD,
    });
    return response.data;
  },

  // Image Processing
  async processImage(imagePath: string, forceReprocess = false): Promise<ProcessImageResponse> {
    const response = await api.post('/api/v1/images/process', {
      image_path: imagePath,
      force_reprocess: forceReprocess,
    }, {
      timeout: TIMEOUTS.PROCESSING,
    });
    return response.data;
  },

  async uploadImage(
    file: File,
    processImmediately = true,
    overwrite = false,
    uploadDir = 'uploads'
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('process_immediately', processImmediately.toString());
    formData.append('overwrite', overwrite.toString());
    formData.append('upload_dir', uploadDir);

    const response = await api.post('/api/v1/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: TIMEOUTS.UPLOAD,
    });
    return response.data;
  },

  async getImageInfo(imageId: string): Promise<ImageInfo> {
    const response = await api.get(`/api/v1/images/info/${imageId}`);
    return response.data;
  },

  async downloadImage(imageId: string): Promise<Blob> {
    const response = await api.get(`/api/v1/images/download/${imageId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  async listImages(limit = 100, offset = 0, objects?: string): Promise<SearchResult[]> {
    const params: any = { limit, offset };
    if (objects) {
      params.objects = objects;
    }
    
    const response = await api.get('/api/v1/images/', { params });
    // API returns images directly as an array, transform to SearchResult format
    return response.data.map((image: any) => ({
      id: image.id,
      image_path: image.path,
      caption: image.caption,
      objects: image.objects,
      distance: 0, // Not applicable for list view
      score: 1.0, // Set to 100% for list view
      metadata: {
        filename: image.filename,
        size: image.size,
        file_size: image.file_size,
        format: image.format,
        processed_at: image.processed_at
      }
    }));
  },

  async deleteImage(imageId: string, deleteFile = false) {
    const response = await api.delete(`/api/v1/images/${imageId}`, {
      params: { delete_file: deleteFile },
    });
    return response.data;
  },

  // Directory Processing
  async processDirectory(
    directoryPath: string,
    forceReprocess = false,
    recursive = false
  ): Promise<DirectoryProcessResponse> {
    const response = await api.post('/api/v1/directories/process', {
      directory_path: directoryPath,
      force_reprocess: forceReprocess,
      recursive,
    }, {
      timeout: TIMEOUTS.PROCESSING,
    });
    return response.data;
  },

  async processDirectoryAsync(
    directoryPath: string,
    forceReprocess = false,
    recursive = false
  ): Promise<{ task_id: string; status: string; message: string }> {
    const response = await api.post('/api/v1/directories/process-async', {
      directory_path: directoryPath,
      force_reprocess: forceReprocess,
      recursive,
    });
    return response.data;
  },

  async getTaskStatus(taskId: string): Promise<Task> {
    const response = await api.get(`/api/v1/directories/task/${taskId}`);
    return response.data;
  },

  async listTasks() {
    const response = await api.get('/api/v1/directories/tasks');
    return response.data;
  },

  async scanDirectory(directoryPath: string, recursive = false) {
    const response = await api.get('/api/v1/directories/scan', {
      params: {
        directory_path: directoryPath,
        recursive,
      },
    });
    return response.data;
  },

  // Search
  async searchImages(
    query: string,
    nResults = 5,
    includeMetadata = true,
    minScore?: number,
    objects?: string,
    searchByContext = true,
    searchByObjects = true
  ): Promise<SearchResponse> {
    // Use the new unified endpoint for search
    const params: any = {
      query,
      limit: nResults,
      include_metadata: includeMetadata,
      search_by_context: searchByContext,
      search_by_objects: searchByObjects,
    };
    
    if (minScore !== undefined && searchByContext) {
      params.min_score = minScore;
    }
    if (objects) {
      params.objects = objects;
    }
    
    const response = await api.get('/api/v1/images/', {
      params,
      timeout: TIMEOUTS.SEARCH,
    });
    
    // Transform response to match SearchResponse interface
    return {
      success: true,
      query,
      total_results: response.data.length,
      results: response.data.map((image: any) => ({
        id: image.id,
        image_path: image.path,
        caption: image.caption,
        objects: image.objects,
        distance: image.distance || 0,
        score: image.score || 1.0,
        metadata: {
          filename: image.filename,
          size: image.size,
          file_size: image.file_size,
          format: image.format,
          processed_at: image.processed_at
        }
      })),
      search_time: 0, // Not provided by new endpoint
      message: `Found ${response.data.length} similar images`
    };
  },


  // Duplicate Detection
  async checkDuplicates(
    imagePath?: string,
    directoryPath?: string,
    similarityThreshold = 0.95
  ) {
    const response = await api.post('/api/v1/duplicates/check', {
      image_path: imagePath,
      directory_path: directoryPath,
      similarity_threshold: similarityThreshold,
    });
    return response.data;
  },

  async compareImages(image1Path: string, image2Path: string) {
    const response = await api.post('/api/v1/duplicates/compare', {
      image1_path: image1Path,
      image2_path: image2Path,
    });
    return response.data;
  },

  async removeDuplicates(
    similarityThreshold = 0.98,
    dryRun = true,
    keepFirst = true
  ) {
    const response = await api.delete('/api/v1/duplicates/remove-duplicates', {
      params: {
        similarity_threshold: similarityThreshold,
        dry_run: dryRun,
        keep_first: keepFirst,
      },
    });
    return response.data;
  },

  async clearAllImages(): Promise<{ success: boolean; message: string }> {
    const response = await api.delete('/api/v1/images/database/clear');
    return response.data;
  },
};

export default apiService;