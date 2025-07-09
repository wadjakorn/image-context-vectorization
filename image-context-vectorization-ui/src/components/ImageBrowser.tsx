import React, { useState, useEffect, useCallback, useRef } from 'react';
import { 
  PhotoIcon, 
  MagnifyingGlassIcon,
  EyeIcon, 
  TrashIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { SearchResult, ImageInfo, apiService } from '../services/api';
import toast from 'react-hot-toast';

interface ImageBrowserProps {
  onImageDelete?: (imageId: string) => void;
  className?: string;
}

interface ImageModalData {
  image: SearchResult;
  imageInfo?: ImageInfo;
  imageUrl?: string;
}

interface ImageThumbnail {
  id: string;
  url: string;
  loading: boolean;
  error: boolean;
}

const ImageBrowser: React.FC<ImageBrowserProps> = ({
  onImageDelete,
  className = '',
}) => {
  const [images, setImages] = useState<SearchResult[]>([]);
  const [selectedImage, setSelectedImage] = useState<ImageModalData | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [loadingImage, setLoadingImage] = useState(false);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [thumbnails, setThumbnails] = useState<Map<string, ImageThumbnail>>(new Map());
  const [loadingThumbnails, setLoadingThumbnails] = useState(false);
  const loadedThumbnailsRef = useRef<Set<string>>(new Set());
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearchMode, setIsSearchMode] = useState(false);
  const [isFilterMode, setIsFilterMode] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [searchOptions, setSearchOptions] = useState({
    limit: 20,
  });

  const searchInputRef = useRef<HTMLInputElement>(null);

  // Load all images on component mount
  useEffect(() => {
    loadAllImages();
  }, []);

  // Load all images
  const loadAllImages = async (objects?: string) => {
    setLoading(true);
    setIsSearchMode(false);
    setIsFilterMode(!!objects);
    try {
      const response = await apiService.listImages(100, 0, objects);
      if (response && Array.isArray(response)) {
        setImages(response);
      } else {
        setImages([]);
      }
    } catch (error) {
      console.error('Failed to load images:', error);
      setImages([]);
      toast.error('Failed to load images. Please check if the API server is running.');
    } finally {
      setLoading(false);
    }
  };


  // Search images
  const handleSearch = async (query: string = searchQuery) => {
    if (!query.trim()) {
      loadAllImages();
      return;
    }

    setSearchLoading(true);
    setIsSearchMode(true);
    setIsFilterMode(false);
    
    try {
      const response = await apiService.searchImages(
        query,
        searchOptions.limit,
      );
      
      if (response && response.results) {
        setImages(response.results);
        toast.success(`Found ${response.results.length} matching images`);
      } else {
        setImages([]);
        toast.error('No images found matching your search');
      }
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed. Please try again.');
    } finally {
      setSearchLoading(false);
    }
  };

  // Handle search input change
  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);
  };

  // Handle form submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(searchQuery);
  };

  // Clear search and filters
  const clearSearch = () => {
    setSearchQuery('');
    setIsSearchMode(false);
    setIsFilterMode(false);
    loadAllImages();
  };


  // Load thumbnail for a single image
  const loadThumbnail = useCallback(async (imageId: string) => {
    if (loadedThumbnailsRef.current.has(imageId)) {
      return;
    }
    
    loadedThumbnailsRef.current.add(imageId);
    
    setThumbnails(prev => new Map(prev.set(imageId, {
      id: imageId,
      url: '',
      loading: true,
      error: false,
    })));

    try {
      const imageBlob = await apiService.downloadImage(imageId);
      const imageUrl = URL.createObjectURL(imageBlob);
      
      setThumbnails(prev => new Map(prev.set(imageId, {
        id: imageId,
        url: imageUrl,
        loading: false,
        error: false,
      })));
    } catch (error) {
      console.error(`Failed to load thumbnail for image ${imageId}:`, error);
      setThumbnails(prev => new Map(prev.set(imageId, {
        id: imageId,
        url: '',
        loading: false,
        error: true,
      })));
    }
  }, []);

  // Load thumbnails when images change
  useEffect(() => {
    const imagesToLoad = images.filter(image => !loadedThumbnailsRef.current.has(image.id));
    
    if (imagesToLoad.length > 0) {
      setLoadingThumbnails(true);
      
      Promise.all(imagesToLoad.map(image => loadThumbnail(image.id)))
        .finally(() => setLoadingThumbnails(false));
    }

    // Cleanup URLs for images no longer in the list
    const currentImageIds = new Set(images.map(img => img.id));
    const thumbnailsToCleanup: string[] = [];
    
    loadedThumbnailsRef.current.forEach(id => {
      if (!currentImageIds.has(id)) {
        thumbnailsToCleanup.push(id);
        loadedThumbnailsRef.current.delete(id);
      }
    });

    if (thumbnailsToCleanup.length > 0) {
      setThumbnails(prev => {
        const newMap = new Map(prev);
        thumbnailsToCleanup.forEach(id => {
          const thumbnail = newMap.get(id);
          if (thumbnail?.url) {
            URL.revokeObjectURL(thumbnail.url);
          }
          newMap.delete(id);
        });
        return newMap;
      });
    }
  }, [images, loadThumbnail]);

  // Load detailed image info function
  const loadImageDetails = useCallback(async (image: SearchResult) => {
    setLoadingImage(true);
    try {
      const [imageInfo, imageBlob] = await Promise.all([
        apiService.getImageInfo(image.id),
        apiService.downloadImage(image.id)
      ]);

      const imageUrl = URL.createObjectURL(imageBlob);
      
      setSelectedImage(prev => prev ? {
        ...prev,
        imageInfo,
        imageUrl
      } : null);
    } catch (error) {
      console.error('Failed to load image details:', error);
      toast.error('Failed to load image details');
    } finally {
      setLoadingImage(false);
    }
  }, []);

  // Load detailed image info when modal opens
  useEffect(() => {
    if (selectedImage && !selectedImage.imageInfo && !selectedImage.imageUrl) {
      loadImageDetails(selectedImage.image);
    }
  }, [selectedImage, loadImageDetails]);

  const openModal = (image: SearchResult, index: number) => {
    setSelectedImage({ image });
    setCurrentImageIndex(index);
  };

  const closeModal = () => {
    if (selectedImage?.imageUrl) {
      URL.revokeObjectURL(selectedImage.imageUrl);
    }
    setSelectedImage(null);
  };

  const navigateImage = (direction: 'prev' | 'next') => {
    const newIndex = direction === 'prev' 
      ? (currentImageIndex - 1 + images.length) % images.length
      : (currentImageIndex + 1) % images.length;
    
    closeModal();
    openModal(images[newIndex], newIndex);
  };

  const handleDeleteImage = async (imageId: string) => {
    if (!window.confirm('Are you sure you want to delete this image?')) return;

    try {
      await apiService.deleteImage(imageId, false);
      toast.success('Image deleted successfully');
      onImageDelete?.(imageId);
      
      if (selectedImage?.image.id === imageId) {
        closeModal();
      }
      
      // Remove from current images list
      setImages(prev => prev.filter(img => img.id !== imageId));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete image';
      toast.error(errorMessage);
    }
  };

  const downloadImage = async (imageId: string, filename: string) => {
    try {
      const blob = await apiService.downloadImage(imageId);
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
      toast.success('Image downloaded successfully');
    } catch (error) {
      toast.error('Failed to download image');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatScore = (score: number) => {
    return `${score.toFixed(1)}%`;
  };

  const getThumbnail = (imageId: string): ImageThumbnail | undefined => {
    return thumbnails.get(imageId);
  };

  const renderImageThumbnail = (image: SearchResult) => {
    const thumbnail = getThumbnail(image.id);
    
    if (!thumbnail || thumbnail.loading) {
      return (
        <div className="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      );
    }
    
    if (thumbnail.error || !thumbnail.url) {
      return (
        <div className="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
          <PhotoIcon className="w-16 h-16 text-gray-400" />
        </div>
      );
    }
    
    return (
      <div className="aspect-square bg-gray-100 dark:bg-gray-700 overflow-hidden">
        <img
          src={thumbnail.url}
          alt={image.caption || 'Image thumbnail'}
          className="w-full h-full object-cover"
          onError={() => {
            setThumbnails(prev => new Map(prev.set(image.id, {
              ...thumbnail,
              error: true,
            })));
          }}
        />
      </div>
    );
  };

  const renderListThumbnail = (image: SearchResult) => {
    const thumbnail = getThumbnail(image.id);
    
    if (!thumbnail || thumbnail.loading) {
      return (
        <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
        </div>
      );
    }
    
    if (thumbnail.error || !thumbnail.url) {
      return (
        <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
          <PhotoIcon className="w-8 h-8 text-gray-400" />
        </div>
      );
    }
    
    return (
      <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
        <img
          src={thumbnail.url}
          alt={image.caption || 'Image thumbnail'}
          className="w-full h-full object-cover"
          onError={() => {
            setThumbnails(prev => new Map(prev.set(image.id, {
              ...thumbnail,
              error: true,
            })));
          }}
        />
      </div>
    );
  };

  return (
    <div className={className}>
      {/* Search Interface */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <form onSubmit={handleSearchSubmit} className="space-y-4">
          <div className="relative">
            <div className="flex">
              <div className="relative flex-1">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  ref={searchInputRef}
                  type="text"
                  value={searchQuery}
                  onChange={handleSearchInputChange}
                  placeholder="Search images using natural language... (e.g., 'cats playing', 'sunset over ocean')"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-l-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <button
                type="submit"
                disabled={searchLoading}
                className="px-6 py-3 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {searchLoading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  'Search'
                )}
              </button>
              
              {(searchQuery || isSearchMode || isFilterMode) && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="ml-2 px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                >
                  Clear
                </button>
              )}
            </div>

          </div>

          {/* Search Options */}
          {/* Advanced Options Toggle */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
            >
              {showAdvanced ? 'Hide' : 'Show'} Advanced Options
            </button>
          </div>

          {/* Advanced Search Options */}
          {showAdvanced && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Max Results
                </label>
                <select
                  value={searchOptions.limit}
                  onChange={(e) => setSearchOptions(prev => ({ ...prev, limit: parseInt(e.target.value) }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value={5}>5 results</option>
                  <option value={10}>10 results</option>
                  <option value={20}>20 results</option>
                  <option value={50}>50 results</option>
                </select>
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Results Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {isSearchMode && isFilterMode 
              ? `Search Results - Filtered by Objects (${images.length})`
              : isSearchMode 
              ? `Search Results (${images.length})`
              : isFilterMode
              ? `Images Filtered by Objects (${images.length})`
              : `All Images (${images.length})`
            }
          </h2>
          
          {/* Loading Indicator */}
          {(loading || loadingThumbnails) && (
            <div className="flex items-center space-x-2 text-blue-600 dark:text-blue-400">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm">
                {loading ? 'Loading images...' : 'Loading thumbnails...'}
              </span>
            </div>
          )}
          
          {/* View Mode Toggle */}
          <div className="flex border border-gray-300 dark:border-gray-600 rounded-lg">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1 text-sm rounded-l-lg ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 text-sm rounded-r-lg ${
                viewMode === 'list'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300'
              }`}
            >
              List
            </button>
          </div>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={() => loadAllImages()}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Empty State */}
      {images.length === 0 && !loading && (
        <div className="text-center py-12">
          <PhotoIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-lg text-gray-600 dark:text-gray-400">
            {isSearchMode && isFilterMode
              ? 'No images found matching your search and object filter'
              : isSearchMode
              ? 'No images found for your search'
              : isFilterMode
              ? 'No images found with the specified objects'
              : 'No images to display'
            }
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
            {isSearchMode || isFilterMode
              ? 'Try adjusting your search terms, object filters, or criteria'
              : 'Upload some images to get started'
            }
          </p>
        </div>
      )}

      {/* Image Gallery */}
      {images.length > 0 && (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {images.map((image, index) => (
                <div
                  key={image.id}
                  className="group relative bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => openModal(image, index)}
                >
                  {/* Image Preview */}
                  {renderImageThumbnail(image)}
                  
                  {/* Image Info */}
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {image.image_path.split('/').pop() || 'Unknown'}
                      </span>
                      {isSearchMode && (
                        <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                          {formatScore(image.score)}
                        </span>
                      )}
                    </div>
                    
                    <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
                      {image.caption}
                    </p>
                    
                    {image.objects && image.objects.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {image.objects.slice(0, 3).map((obj, objIndex) => (
                          <span
                            key={objIndex}
                            className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded-full"
                          >
                            {obj}
                          </span>
                        ))}
                        {image.objects.length > 3 && (
                          <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                            +{image.objects.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="flex space-x-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          openModal(image, index);
                        }}
                        className="p-1 bg-white dark:bg-gray-800 rounded-full shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                        title="View details"
                      >
                        <EyeIcon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteImage(image.id);
                        }}
                        className="p-1 bg-white dark:bg-gray-800 rounded-full shadow-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                        title="Delete"
                      >
                        <TrashIcon className="w-4 h-4 text-red-600 dark:text-red-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            /* List View */
            <div className="space-y-4">
              {images.map((image, index) => (
                <div
                  key={image.id}
                  className="flex items-center space-x-4 p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => openModal(image, index)}
                >
                  {/* Image Thumbnail */}
                  <div className="w-16 h-16 flex-shrink-0">
                    {renderListThumbnail(image)}
                  </div>
                  
                  {/* Image Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {image.image_path.split('/').pop() || 'Unknown'}
                      </h3>
                      {isSearchMode && (
                        <span className="text-sm text-green-600 dark:text-green-400 font-medium">
                          {formatScore(image.score)}
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
                      {image.caption}
                    </p>
                    
                    {image.objects && image.objects.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {image.objects.slice(0, 5).map((obj, objIndex) => (
                          <span
                            key={objIndex}
                            className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded-full"
                          >
                            {obj}
                          </span>
                        ))}
                        {image.objects.length > 5 && (
                          <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-full">
                            +{image.objects.length - 5}
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        downloadImage(image.id, image.image_path.split('/').pop() || 'image');
                      }}
                      className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                      title="Download"
                    >
                      <ArrowDownTrayIcon className="w-4 h-4" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteImage(image.id);
                      }}
                      className="p-2 text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                      title="Delete"
                    >
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-6xl max-h-[90vh] w-full flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {selectedImage.image.image_path.split('/').pop() || 'Image Details'}
              </h3>
              <div className="flex items-center space-x-2">
                {/* Navigation Buttons */}
                <button
                  onClick={() => navigateImage('prev')}
                  className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                  title="Previous image"
                >
                  <ChevronLeftIcon className="w-5 h-5" />
                </button>
                <button
                  onClick={() => navigateImage('next')}
                  className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                  title="Next image"
                >
                  <ChevronRightIcon className="w-5 h-5" />
                </button>
                <button
                  onClick={closeModal}
                  className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="flex-1 flex overflow-hidden">
              {/* Image Display */}
              <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
                {loadingImage ? (
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600 dark:text-gray-400">Loading image...</span>
                  </div>
                ) : selectedImage.imageUrl ? (
                  <img
                    src={selectedImage.imageUrl}
                    alt={selectedImage.image.caption}
                    className="max-w-full max-h-full object-contain"
                  />
                ) : (
                  <div className="text-center">
                    <PhotoIcon className="w-24 h-24 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">Image not available</p>
                  </div>
                )}
              </div>

              {/* Image Metadata */}
              <div className="w-80 p-4 border-l border-gray-200 dark:border-gray-700 overflow-y-auto">
                <div className="space-y-4">
                  {/* Basic Info */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                      Basic Information
                    </h4>
                    <div className="space-y-2 text-sm">
                      {isSearchMode && (
                        <div className="flex justify-between">
                          <span className="text-gray-600 dark:text-gray-400">Match Score:</span>
                          <span className="text-green-600 dark:text-green-400 font-medium">
                            {formatScore(selectedImage.image.score)}
                          </span>
                        </div>
                      )}
                      {selectedImage.imageInfo && (
                        <>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Size:</span>
                            <span className="text-gray-900 dark:text-white">
                              {selectedImage.imageInfo.size[0]} × {selectedImage.imageInfo.size[1]}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">File Size:</span>
                            <span className="text-gray-900 dark:text-white">
                              {formatFileSize(selectedImage.imageInfo.file_size)}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600 dark:text-gray-400">Format:</span>
                            <span className="text-gray-900 dark:text-white">
                              {selectedImage.imageInfo.format}
                            </span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Caption */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                      Caption
                    </h4>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {selectedImage.image.caption}
                    </p>
                  </div>

                  {/* Objects */}
                  {selectedImage.image.objects && selectedImage.image.objects.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                        Detected Objects
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {selectedImage.image.objects.map((obj, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-xs rounded-full"
                          >
                            {obj}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Metadata */}
                  {selectedImage.image.metadata && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                        Additional Metadata
                      </h4>
                      <div className="text-xs text-gray-600 dark:text-gray-400 font-mono bg-gray-50 dark:bg-gray-900 p-2 rounded">
                        <pre className="whitespace-pre-wrap">{JSON.stringify(selectedImage.image.metadata, null, 2)}</pre>
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => downloadImage(selectedImage.image.id, selectedImage.image.image_path.split('/').pop() || 'image')}
                        className="flex-1 flex items-center justify-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
                      >
                        <ArrowDownTrayIcon className="w-4 h-4 mr-1" />
                        Download
                      </button>
                      <button
                        onClick={() => handleDeleteImage(selectedImage.image.id)}
                        className="flex-1 flex items-center justify-center px-3 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
                      >
                        <TrashIcon className="w-4 h-4 mr-1" />
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageBrowser;