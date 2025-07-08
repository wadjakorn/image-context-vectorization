#!/usr/bin/env python3
"""
Examples of using the Image Context Extractor API.
"""
import asyncio
import aiohttp
import json
import os
from pathlib import Path
import websockets


# API Configuration
API_BASE_URL = "http://localhost:8000"
WS_BASE_URL = "ws://localhost:8000"


async def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing health check...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/api/v1/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Service is {data['status']}")
                print(f"   Version: {data['version']}")
                print(f"   Database: {'Connected' if data['database_connected'] else 'Disconnected'}")
                print(f"   Models: {'Loaded' if data['models_loaded'] else 'Not loaded'}")
                print(f"   Uptime: {data['uptime']:.2f} seconds")
            else:
                print(f"❌ Health check failed: {response.status}")


async def test_image_upload():
    """Test image upload functionality."""
    print("\n📤 Testing image upload...")
    
    # Create a test image file (you can replace this with an actual image)
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"⚠️  Test image not found: {test_image_path}")
        print("   Please place a test image file or update the path")
        return None
    
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        data.add_field('file', 
                      open(test_image_path, 'rb'),
                      filename=os.path.basename(test_image_path),
                      content_type='image/jpeg')
        data.add_field('process_immediately', 'true')
        
        async with session.post(f"{API_BASE_URL}/api/v1/images/upload", data=data) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Image uploaded successfully")
                print(f"   Filename: {result['filename']}")
                print(f"   File path: {result['file_path']}")
                print(f"   File size: {result['file_size']} bytes")
                if result['image_id']:
                    print(f"   Image ID: {result['image_id']}")
                return result['image_id']
            else:
                error = await response.json()
                print(f"❌ Upload failed: {error}")
                return None


async def test_image_processing():
    """Test image processing endpoint."""
    print("\n🔄 Testing image processing...")
    
    # Use an existing image path (update this to your test image)
    test_image_path = "/Users/wadjakorntonsri/Downloads/google image search/fastfood.webp"
    
    if not os.path.exists(test_image_path):
        print(f"⚠️  Test image not found: {test_image_path}")
        print("   Please update the path to an existing image")
        return None
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "image_path": test_image_path,
            "force_reprocess": False
        }
        
        async with session.post(f"{API_BASE_URL}/api/v1/images/process", 
                               json=payload) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Image processed successfully")
                print(f"   Image ID: {result['image_id']}")
                print(f"   Processing time: {result['processing_time']:.2f} seconds")
                print(f"   Was duplicate: {result['was_duplicate']}")
                if result['image_info']:
                    print(f"   Caption: {result['image_info']['caption']}")
                    print(f"   Objects: {', '.join(result['image_info']['objects'])}")
                return result['image_id']
            else:
                error = await response.json()
                print(f"❌ Processing failed: {error}")
                return None


async def test_search():
    """Test search functionality."""
    print("\n🔍 Testing search...")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "query": "food",
            "n_results": 3,
            "include_metadata": True
        }
        
        async with session.post(f"{API_BASE_URL}/api/v1/search/", 
                               json=payload) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Search completed in {result['search_time']:.2f} seconds")
                print(f"   Query: {result['query']}")
                print(f"   Results found: {result['total_results']}")
                
                for i, item in enumerate(result['results'], 1):
                    print(f"   {i}. {os.path.basename(item['image_path'])}")
                    print(f"      Caption: {item['caption']}")
                    print(f"      Score: {item['score']:.3f}")
                    print(f"      Objects: {', '.join(item['objects'])}")
                    print()
            else:
                error = await response.json()
                print(f"❌ Search failed: {error}")


async def test_directory_scan():
    """Test directory scanning."""
    print("\n📁 Testing directory scan...")
    
    # Update this to your test directory
    test_directory = "/Users/wadjakorntonsri/Downloads/google image search/"
    
    if not os.path.exists(test_directory):
        print(f"⚠️  Test directory not found: {test_directory}")
        print("   Please update the path to an existing directory")
        return
    
    async with aiohttp.ClientSession() as session:
        params = {
            "directory_path": test_directory,
            "recursive": False
        }
        
        async with session.get(f"{API_BASE_URL}/api/v1/directories/scan", 
                              params=params) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Directory scanned successfully")
                print(f"   Directory: {result['directory_path']}")
                print(f"   Total files: {result['total_files']}")
                print(f"   Already processed: {result['already_processed']}")
                print(f"   New files: {result['new_files']}")
                print(f"   Supported formats: {', '.join(result['supported_formats'])}")
            else:
                error = await response.json()
                print(f"❌ Directory scan failed: {error}")


async def test_duplicate_check():
    """Test duplicate detection."""
    print("\n🔍 Testing duplicate detection...")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "similarity_threshold": 0.95
        }
        
        async with session.post(f"{API_BASE_URL}/api/v1/duplicates/check", 
                               json=payload) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Duplicate check completed in {result['check_time']:.2f} seconds")
                print(f"   Total images checked: {result['total_images']}")
                print(f"   Duplicate groups found: {len(result['duplicate_groups'])}")
                print(f"   Total duplicates: {result['total_duplicates']}")
                
                for i, group in enumerate(result['duplicate_groups'], 1):
                    print(f"   Group {i}:")
                    print(f"     Representative: {os.path.basename(group['paths'][0])}")
                    for j, dup_path in enumerate(group['paths'][1:], 1):
                        score = group['similarity_scores'][j-1] if j-1 < len(group['similarity_scores']) else 'N/A'
                        print(f"     Duplicate {j}: {os.path.basename(dup_path)} (score: {score:.3f})")
            else:
                error = await response.json()
                print(f"❌ Duplicate check failed: {error}")


async def test_websocket():
    """Test WebSocket connection."""
    print("\n🔌 Testing WebSocket connection...")
    
    try:
        uri = f"{WS_BASE_URL}/ws"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Send a ping
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   Received: {data['type']}")
            
            # Subscribe to a channel
            await websocket.send(json.dumps({
                "type": "subscribe",
                "channel": "processing"
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"   Subscription: {data.get('message', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")


async def test_api_info():
    """Test API info endpoint."""
    print("\n📋 Testing API info...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/api/v1/info") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ API Info retrieved")
                print(f"   Name: {result['name']}")
                print(f"   Version: {result['version']}")
                print(f"   Features: {len(result['features'])}")
                for feature in result['features']:
                    print(f"     - {feature}")
            else:
                print(f"❌ API info failed: {response.status}")


async def main():
    """Run all API tests."""
    print("🧪 Image Context Extractor API Examples")
    print("=" * 50)
    
    # Test individual endpoints
    await test_health_check()
    await test_api_info()
    
    # Test core functionality
    image_id = await test_image_processing()
    await test_search()
    await test_directory_scan()
    await test_duplicate_check()
    
    # Test upload if no image was processed
    if not image_id:
        await test_image_upload()
    
    # Test WebSocket
    await test_websocket()
    
    print("\n✅ All API tests completed!")
    print(f"📚 Visit {API_BASE_URL}/docs for interactive API documentation")


if __name__ == "__main__":
    print("🚀 Starting API examples...")
    print("Make sure the API server is running: python run_api.py")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Examples stopped by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        print("Make sure the API server is running and accessible")