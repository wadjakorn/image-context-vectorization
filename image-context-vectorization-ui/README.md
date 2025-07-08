# Image Context Vectorization UI

A modern React frontend for the Image Context Vectorization API that provides AI-powered image processing, search, and management capabilities.

## Features

- **🖼️ Image Upload**: Drag-and-drop interface for uploading single or multiple images
- **🔍 AI-Powered Search**: Search images using natural language descriptions
- **🖥️ Image Gallery**: Browse and manage your image collection with detailed metadata
- **📊 Processing Status**: Real-time monitoring of image processing tasks
- **🤖 Model Management**: Monitor AI model loading status and preload for performance
- **🔄 Duplicate Detection**: Find and manage duplicate images
- **📁 Directory Processing**: Batch process entire directories of images
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices
- **🌙 Dark Mode**: Modern dark/light theme support

## Prerequisites

- Node.js 16+ and npm
- Image Context Vectorization API running on `http://localhost:8000` (or configured URL)

## Quick Start

1. **Clone and Install**
   ```bash
   cd image-context-ui
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env to set your API URL if different from default
   ```

3. **Start Development Server**
   ```bash
   npm start
   ```

4. **Open Your Browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Configuration

Create a `.env` file in the project root:

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Optional: Enable debug logging
REACT_APP_DEBUG=false
```

### Environment Variables

- `REACT_APP_API_URL`: Base URL of the Image Context Vectorization API
- `REACT_APP_DEBUG`: Enable debug logging (default: false)

**Timeout Configuration (in milliseconds):**
- `REACT_APP_API_TIMEOUT`: Default API timeout (30 seconds)
- `REACT_APP_UPLOAD_TIMEOUT`: File upload timeout (2 minutes)
- `REACT_APP_SEARCH_TIMEOUT`: Image search timeout (1 minute)
- `REACT_APP_PROCESSING_TIMEOUT`: Image processing timeout (5 minutes)
- `REACT_APP_MODEL_PRELOAD_TIMEOUT`: Model preloading timeout (3 minutes)
- `REACT_APP_HEALTH_TIMEOUT`: Health check timeout (10 seconds)

## Usage

### 1. Upload Images
- Navigate to the **Upload** tab
- Drag and drop images or click to select files
- Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP
- Maximum file size: 10MB per image
- Upload up to 10 images at once

### 2. Search Images
- Go to the **Search** tab
- Enter natural language descriptions like:
  - "cats playing"
  - "sunset over ocean"
  - "people at a party"
  - "red car on highway"
- Use advanced search options for:
  - Number of results
  - Minimum similarity score
  - Metadata inclusion

### 3. Browse Gallery
- **Gallery** tab shows all your images with actual thumbnails
- Switch between grid and list view
- Automatic thumbnail loading with progress indicators
- Click images for detailed view with:
  - Full-size image display
  - AI-generated captions
  - Detected objects and tags
  - File metadata
  - Similarity scores (for search results)
- Download or delete images
- Memory-efficient image caching and cleanup

### 4. Monitor Processing
- **Processing** tab shows:
  - Real-time task status
  - Processing statistics
  - Task history
  - Error details
- Auto-refresh or manual refresh options

### 5. Model Management
- **Models** tab provides:
  - Real-time model loading status
  - Device information (CPU/GPU)
  - Model preloading functionality
  - Loading time statistics
  - Memory usage insights
- Preload models for faster processing
- Monitor individual model status

### 6. Directory Processing
- **Directory** tab (coming soon)
- Batch process entire folders
- Background task management

## API Integration

The UI integrates with the Image Context Vectorization API endpoints:

- `/api/v1/health` - Health status
- `/api/v1/images/upload` - Image upload
- `/api/v1/images/process` - Process images
- `/api/v1/search/` - Search images
- `/api/v1/duplicates/check` - Duplicate detection
- `/api/v1/models/status` - Model loading status
- `/api/v1/models/preload` - Preload all models
- WebSocket endpoints for real-time updates

## Component Architecture

```
src/
├── components/
│   ├── ImageUpload.tsx      # Drag-and-drop upload
│   ├── ImageSearch.tsx      # Search interface
│   ├── ImageGallery.tsx     # Gallery with modal
│   ├── ProcessingStatus.tsx # Task monitoring
│   └── ModelManagement.tsx  # Model status and preloading
├── services/
│   └── api.ts              # API client
└── App.tsx                 # Main application
```

### Key Components

- **ImageUpload**: Handles file uploads with progress tracking
- **ImageSearch**: Search interface with suggestions and filters
- **ImageGallery**: Grid/list view with detailed image modal
- **ProcessingStatus**: Real-time task monitoring
- **ModelManagement**: AI model status monitoring and preloading
- **ApiService**: Centralized API communication

## Development

### Available Scripts

- `npm start` - Development server (http://localhost:3000)
- `npm test` - Run test suite
- `npm run build` - Production build
- `npm run eject` - Eject from Create React App (irreversible)

### Technology Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Heroicons** for icons
- **React Dropzone** for file uploads
- **React Hot Toast** for notifications
- **Axios** for API requests

### Code Style

- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting (if configured)
- Modern React with hooks
- Responsive design patterns

## Production Deployment

1. **Build for Production**
   ```bash
   npm run build
   ```

2. **Serve Static Files**
   ```bash
   # Using serve
   npm install -g serve
   serve -s build -l 3000
   
   # Or using nginx, Apache, etc.
   ```

3. **Environment Configuration**
   - Set `REACT_APP_API_URL` to your production API URL
   - Configure CORS on your API server for the frontend domain

## Performance Optimizations

The frontend includes several optimizations to minimize API calls and improve performance:

- **Request Deduplication**: Prevents duplicate API calls for the same data
- **Caching**: Popular tags are cached for 5 minutes to reduce server load
- **Debounced Search**: Search suggestions are debounced by 500ms to prevent excessive typing requests
- **Single Load Pattern**: Uses `useRef` to ensure one-time loading of popular tags
- **Error Handling**: Graceful degradation when API is unavailable
- **Configurable Timeouts**: Operation-specific timeouts with visual indicators
- **Timeout Warnings**: Visual feedback when operations approach timeout limits

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if the backend API is running
   - Verify `REACT_APP_API_URL` in `.env`
   - Check CORS configuration on API server

2. **Images Not Loading**
   - Ensure API image download endpoints are working
   - Check browser network tab for failed requests
   - Verify image file permissions
   - Thumbnails load automatically - look for loading spinners
   - Check browser console for image loading errors

3. **Upload Failures**
   - Check file size limits (10MB default)
   - Verify supported file formats
   - Check API upload endpoint

4. **Search Not Working**
   - Ensure images have been processed first
   - Check if vector database is connected
   - Verify search API endpoints

5. **Models Not Loading**
   - Check model management tab for loading status
   - Preload models manually if needed
   - Verify model files are available on server
   - Check device configuration (CPU/GPU)

6. **Slow Processing Performance**
   - Use model preloading before processing images
   - Check if models are loaded in memory
   - Consider GPU acceleration if available
   - Monitor model loading times

7. **Request Timeouts**
   - Operations have different timeout limits based on complexity
   - Visual timeout indicators show progress and warnings
   - Configure timeouts via environment variables if needed
   - Check network connection if timeouts occur frequently

8. **Duplicate API Calls (Development)**
   - Normal in React development mode due to Strict Mode
   - Optimizations prevent actual duplicate requests to server
   - Production builds will not show this behavior

### Debug Mode

Enable debug logging by setting `REACT_APP_DEBUG=true` in `.env`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Image Context Vectorization system.

---

## Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### Available Scripts

In the project directory, you can run:

#### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

#### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

#### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

#### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).