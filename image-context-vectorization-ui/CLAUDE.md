# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a React TypeScript frontend for the Image Context Vectorization API - an AI-powered image management system that enables natural language search, object filtering, and automated processing of image collections.

## Essential Commands

### Development
```bash
npm install              # Install dependencies
npm start               # Start development server (http://localhost:3000)
npm run build          # Build for production
npm test               # Run test suite
```

### Backend Dependency
The frontend requires the Image Context Vectorization API running on `http://localhost:8000` (configurable via `REACT_APP_API_URL`).

## Architecture Overview

### Core Structure
- **App.tsx**: Main application with tabbed interface (Upload → Browse & Search → Processing → Models → Directory)
- **src/services/api.ts**: Centralized API client with TypeScript interfaces for all backend endpoints
- **src/components/**: Specialized UI components for each major feature area

### Key Components

**ImageBrowser.tsx** (700+ lines) - The unified interface combining search and gallery functionality:
- Handles both text search and object filtering via the unified `/api/v1/images/` endpoint
- Manages image thumbnails with memory-efficient blob URL handling
- Supports grid/list view modes with detailed image modals
- Contains complex state management for search modes, filters, and loading states

**ImageUpload.tsx** - Drag-and-drop upload with progress tracking:
- Supports multiple files (up to 10 images, 10MB each)
- Integrates with react-dropzone for file handling
- Provides per-file progress indicators

**ModelManagement.tsx** - AI model preloading and status monitoring:
- Real-time model loading status (BLIP, CLIP, Sentence Transformer)
- Performance timing and device information
- Critical for optimizing image processing performance

**ProcessingStatus.tsx** - Task monitoring and background processing status

### API Integration Architecture

The frontend uses a unified API endpoint strategy:
- **Unified Endpoint**: `/api/v1/images/` serves both listing and search with query parameters
- **Object Filtering**: Supports comma-separated object filters (e.g., `objects=cat,dog,person`)
- **Search + Filter**: Combines text queries with object filtering
- **Response Transformation**: API responses are normalized to consistent `SearchResult[]` format

### State Management Patterns

1. **Thumbnail Management**: Uses `Map<string, ImageThumbnail>` with `useRef` for tracking loaded images
2. **Memory Management**: Automatic cleanup of blob URLs when images change
3. **Request Deduplication**: Prevents duplicate API calls during rapid state changes
4. **Mode Switching**: Clear distinction between browse, search, and filter modes

### Performance Optimizations

- **Lazy Thumbnail Loading**: Images load thumbnails on-demand via `/api/v1/images/download/{id}`
- **Operation-Specific Timeouts**: Different timeout values for uploads, searches, processing (configurable via environment variables)
- **useCallback Optimization**: Critical functions are memoized to prevent unnecessary re-renders
- **Memory Cleanup**: Automatic revocation of object URLs when components unmount

## Environment Configuration

Required environment variables (see `.env.example`):
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000
REACT_APP_UPLOAD_TIMEOUT=120000
REACT_APP_SEARCH_TIMEOUT=60000
REACT_APP_PROCESSING_TIMEOUT=300000
REACT_APP_MODEL_PRELOAD_TIMEOUT=180000
REACT_APP_HEALTH_TIMEOUT=10000
```

## Key Technical Details

### TypeScript Interfaces
- **SearchResult**: Core interface for both search results and gallery items
- **ImageInfo**: Detailed metadata from `/api/v1/images/info/{id}`
- **SearchResponse**: Wrapper for search API responses
- **HealthResponse**: System status and database connection info

### API Service Pattern
The `apiService` object in `src/services/api.ts` provides:
- Type-safe method signatures with proper error handling
- Automatic response transformation from API format to frontend interfaces
- Timeout configuration per operation type
- Object filtering support in both `listImages()` and `searchImages()` methods

### Component Communication
- Upload completion triggers navigation to Browse tab
- Image deletion updates are propagated through callback props
- Global toast notifications for user feedback
- Health status monitoring with visual indicators

### Critical Implementation Notes

1. **Image Loading**: The `loadThumbnail` function in ImageBrowser must use `useCallback` to prevent infinite re-renders
2. **Object Filtering**: The `objects` parameter accepts comma-separated values with case-insensitive matching
3. **Modal Management**: Image modals require proper cleanup of blob URLs to prevent memory leaks
4. **Search vs Filter Modes**: Clear state distinction prevents UI confusion between different operation modes

## Styling & UI Framework

- **Tailwind CSS** with dark mode support
- **Heroicons** for consistent iconography
- **React Hot Toast** for notifications
- **Responsive Design** with mobile-first approach
- **Grid/List Views** with smooth transitions

## File Upload Constraints

- **Supported Formats**: PNG, JPG, JPEG, GIF, BMP, WebP
- **File Size Limit**: 10MB per image
- **Batch Upload**: Maximum 10 files simultaneously
- **Processing**: Automatic AI processing on upload (configurable)