import React, { useState, useCallback, useEffect, useRef } from 'react';
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import { apiService, SearchResponse, SearchResult } from '../services/api';
import TimeoutIndicator from './TimeoutIndicator';
import toast from 'react-hot-toast';

interface ImageSearchProps {
  onSearchComplete?: (results: SearchResult[]) => void;
  className?: string;
}

const ImageSearch: React.FC<ImageSearchProps> = ({
  onSearchComplete,
  className = '',
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  // const [suggestions, setSuggestions] = useState<string[]>([]);
  // const [popularTags, setPopularTags] = useState<string[]>([]);
  // const popularTagsLoadedRef = useRef(false);
  
  // Advanced search options
  const [nResults, setNResults] = useState(5);
  const [minScore, setMinScore] = useState<number | undefined>(undefined);
  const [includeMetadata, setIncludeMetadata] = useState(true);

  // Search statistics
  const [searchStats, setSearchStats] = useState<{
    totalResults: number;
    searchTime: number;
    query: string;
  } | null>(null);

  // Load popular tags on component mount
  useEffect(() => {
    // const loadPopularTags = async () => {
    //   if (popularTagsLoadedRef.current) return; // Prevent duplicate calls
    //   popularTagsLoadedRef.current = true;
      
    //   try {
    //     const response = await apiService.getPopularTags(20);
    //     setPopularTags(response.tags || []);
    //   } catch (error) {
    //     console.error('Failed to load popular tags:', error);
    //   }
    // };
    
    // loadPopularTags();
  }, []); // Empty dependency array - only run once

  // Get search suggestions as user types
  // const getSuggestions = useCallback(async (searchQuery: string) => {
  //   if (searchQuery.length < 2) {
  //     setSuggestions([]);
  //     return;
  //   }

  //   try {
  //     const response = await apiService.getSearchSuggestions(searchQuery, 10);
  //     setSuggestions(response.suggestions || []);
  //   } catch (error) {
  //     // Fail silently for suggestions to avoid spamming user with errors
  //     console.error('Failed to get suggestions:', error);
  //     setSuggestions([]);
  //   }
  // }, []);

  // Debounced suggestions
  // useEffect(() => {
  //   const timer = setTimeout(() => {
  //     if (query.trim() && query.length >= 2) {
  //       getSuggestions(query);
  //     } else {
  //       setSuggestions([]);
  //     }
  //   }, 500); // Increased debounce time to reduce API calls

  //   return () => clearTimeout(timer);
  // }, [query, getSuggestions]);

  const handleSearch = async (searchQuery: string = query) => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    // setSuggestions([]);

    try {
      const response: SearchResponse = await apiService.searchImages(
        searchQuery,
        nResults,
        includeMetadata,
        minScore
      );

      setResults(response.results);
      setSearchStats({
        totalResults: response.total_results,
        searchTime: response.search_time,
        query: response.query,
      });

      onSearchComplete?.(response.results);

      if (response.results.length === 0) {
        toast('No images found matching your search', {
          icon: 'ℹ️',
        });
      } else {
        toast.success(`Found ${response.results.length} images`);
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Search failed';
      toast.error(`Search failed: ${errorMessage}`);
      setResults([]);
      setSearchStats(null);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // const handleTagClick = (tag: string) => {
  //   setQuery(tag);
  //   handleSearch(tag);
  // };

  // const handleSuggestionClick = (suggestion: string) => {
  //   setQuery(suggestion);
  //   handleSearch(suggestion);
  // };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setSearchStats(null);
    // setSuggestions([]);
    onSearchComplete?.([]);
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Search images by content, objects, or description..."
            className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600 dark:text-white"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              title="Advanced search options"
            >
              <AdjustmentsHorizontalIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search Suggestions */}
        {/* {suggestions.length > 0 && (
          <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full px-4 py-2 text-left hover:bg-gray-100 dark:hover:bg-gray-700 focus:bg-gray-100 dark:focus:bg-gray-700 focus:outline-none"
              >
                <div className="flex items-center space-x-2">
                  <MagnifyingGlassIcon className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-900 dark:text-white">{suggestion}</span>
                </div>
              </button>
            ))}
          </div>
        )} */}
      </div>

      {/* Advanced Search Options */}
      {showAdvanced && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Advanced Search Options
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Number of Results
              </label>
              <select
                value={nResults}
                onChange={(e) => setNResults(parseInt(e.target.value))}
                className="w-full border border-gray-300 rounded-md px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
                <option value={50}>50</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Minimum Score
              </label>
              <input
                type="number"
                value={minScore || ''}
                onChange={(e) => setMinScore(e.target.value ? parseFloat(e.target.value) : undefined)}
                placeholder="0.0 - 1.0"
                min="0"
                max="1"
                step="0.1"
                className="w-full border border-gray-300 rounded-md px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeMetadata"
                checked={includeMetadata}
                onChange={(e) => setIncludeMetadata(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="includeMetadata" className="text-sm text-gray-700 dark:text-gray-300">
                Include metadata
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Search Button */}
      <div className="mt-4 flex items-center justify-between">
        <button
          onClick={() => handleSearch()}
          disabled={loading || !query.trim()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <MagnifyingGlassIcon className="w-4 h-4" />
          )}
          <span>{loading ? 'Searching...' : 'Search'}</span>
        </button>

        {(results.length > 0 || query) && (
          <button
            onClick={clearSearch}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
          >
            Clear
          </button>
        )}
      </div>

      {/* Timeout Indicator */}
      <TimeoutIndicator
        isLoading={loading}
        operation="search"
        onTimeout={() => toast.error('Search is taking longer than expected')}
      />

      {/* Search Statistics */}
      {searchStats && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <span className="text-blue-700 dark:text-blue-300">
              Found {searchStats.totalResults} results for "{searchStats.query}"
            </span>
            <span className="text-blue-600 dark:text-blue-400">
              {searchStats.searchTime.toFixed(2)}s
            </span>
          </div>
        </div>
      )}

      {/* Popular Tags */}
      {/* {popularTags.length > 0 && results.length === 0 && !loading && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
            Popular Tags
          </h3>
          <div className="flex flex-wrap gap-2">
            {popularTags.map((tag, index) => (
              <button
                key={index}
                onClick={() => handleTagClick(tag)}
                className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )} */}

      {/* No Results Message */}
      {results.length === 0 && searchStats && !loading && (
        <div className="mt-6 text-center py-8">
          <MagnifyingGlassIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-lg text-gray-600 dark:text-gray-400">
            No images found matching your search
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-500 mt-2">
            Try different keywords or check your spelling
          </p>
        </div>
      )}
    </div>
  );
};

export default ImageSearch;