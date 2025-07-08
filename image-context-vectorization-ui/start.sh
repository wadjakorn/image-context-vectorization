#!/bin/bash

echo "🚀 Starting Image Context Vectorization UI..."
echo "📡 API URL: ${REACT_APP_API_URL:-http://localhost:8000}"
echo "🌐 Frontend URL: http://localhost:3000"
echo ""
echo "Make sure your backend API is running on ${REACT_APP_API_URL:-http://localhost:8000}"
echo ""

npm start