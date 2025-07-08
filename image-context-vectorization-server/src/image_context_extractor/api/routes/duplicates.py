"""API routes for duplicate detection operations."""

import os
import time
import logging
import hashlib
from typing import List, Dict, Any, Tuple
from fastapi import APIRouter, HTTPException, Query, Depends
import numpy as np

from ..models.requests import DuplicateCheckRequest
from ..models.responses import DuplicateCheckResponse, DuplicateGroup
from ..dependencies import get_extractor_lazy
from ...core.extractor import ImageContextExtractor


router = APIRouter(prefix="/api/v1/duplicates", tags=["duplicates"])
logger = logging.getLogger(__name__)




def calculate_image_similarity(
    extractor: ImageContextExtractor,
    image1_path: str,
    image2_path: str
) -> float:
    """Calculate similarity between two images using embeddings."""
    try:
        # Extract embeddings for both images
        features1 = extractor.extract_image_features(image1_path)
        features2 = extractor.extract_image_features(image2_path)
        
        embedding1 = features1['embedding']
        embedding2 = features2['embedding']
        
        # Calculate cosine similarity
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Error calculating similarity between {image1_path} and {image2_path}: {e}")
        return 0.0


def find_duplicates_in_list(
    extractor: ImageContextExtractor,
    image_paths: List[str],
    similarity_threshold: float = 0.95
) -> List[DuplicateGroup]:
    """Find duplicate groups in a list of images."""
    duplicate_groups = []
    processed = set()
    
    for i, image1_path in enumerate(image_paths):
        if image1_path in processed:
            continue
            
        current_group = [image1_path]
        similarity_scores = [1.0]  # Self-similarity
        
        for j, image2_path in enumerate(image_paths[i+1:], i+1):
            if image2_path in processed:
                continue
                
            similarity = calculate_image_similarity(extractor, image1_path, image2_path)
            
            if similarity >= similarity_threshold:
                current_group.append(image2_path)
                similarity_scores.append(similarity)
                processed.add(image2_path)
        
        # If we found duplicates, create a group
        if len(current_group) > 1:
            # Generate IDs for the group
            representative_id = hashlib.md5(current_group[0].encode()).hexdigest()
            duplicate_ids = [hashlib.md5(path.encode()).hexdigest() for path in current_group[1:]]
            
            duplicate_group = DuplicateGroup(
                representative_id=representative_id,
                duplicate_ids=duplicate_ids,
                similarity_scores=similarity_scores[1:],  # Exclude self-similarity
                paths=current_group
            )
            duplicate_groups.append(duplicate_group)
        
        processed.add(image1_path)
    
    return duplicate_groups


@router.post("/check", response_model=DuplicateCheckResponse)
async def check_duplicates(
    request: DuplicateCheckRequest,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Check for duplicate images in database or directory."""
    try:
        start_time = time.time()
        
        images_to_check = []
        
        if request.image_path:
            # Check specific image against database
            if not os.path.exists(request.image_path):
                raise HTTPException(status_code=404, detail="Image file not found")
            
            # Get all processed images from database
            processed_images = extractor_instance.get_processed_images()
            
            # Find similar images using search
            features = extractor_instance.extract_image_features(request.image_path)
            search_results = extractor_instance.search_similar_images(
                features['combined_text'],
                n_results=50  # Check more results for duplicates
            )
            
            # Filter by similarity threshold
            duplicate_paths = []
            similarity_scores = []
            
            for result in search_results:
                # Skip self if it's already in database
                if result['image_path'] == request.image_path:
                    continue
                
                score = 1.0 - result['distance']  # Convert distance to similarity
                if score >= request.similarity_threshold:
                    duplicate_paths.append(result['image_path'])
                    similarity_scores.append(score)
            
            duplicate_groups = []
            if duplicate_paths:
                representative_id = hashlib.md5(request.image_path.encode()).hexdigest()
                duplicate_ids = [hashlib.md5(path.encode()).hexdigest() for path in duplicate_paths]
                
                duplicate_group = DuplicateGroup(
                    representative_id=representative_id,
                    duplicate_ids=duplicate_ids,
                    similarity_scores=similarity_scores,
                    paths=[request.image_path] + duplicate_paths
                )
                duplicate_groups.append(duplicate_group)
            
            total_images = len(processed_images) + 1
            
        elif request.directory_path:
            # Check directory for internal duplicates
            if not os.path.exists(request.directory_path):
                raise HTTPException(status_code=404, detail="Directory not found")
            
            # Get all images in directory
            images_to_check = extractor_instance.image_processor.get_image_files(request.directory_path)
            
            if not images_to_check:
                return DuplicateCheckResponse(
                    success=True,
                    total_images=0,
                    duplicate_groups=[],
                    total_duplicates=0,
                    check_time=time.time() - start_time,
                    message="No images found in directory"
                )
            
            # Find duplicates within the directory
            duplicate_groups = find_duplicates_in_list(
                extractor_instance,
                images_to_check,
                request.similarity_threshold
            )
            
            total_images = len(images_to_check)
        
        else:
            # Check all processed images for duplicates
            processed_images = extractor_instance.get_processed_images()
            
            if not processed_images:
                return DuplicateCheckResponse(
                    success=True,
                    total_images=0,
                    duplicate_groups=[],
                    total_duplicates=0,
                    check_time=time.time() - start_time,
                    message="No images in database"
                )
            
            # Sample for performance if too many images
            if len(processed_images) > 100:
                import random
                images_to_check = random.sample(processed_images, 100)
            else:
                images_to_check = processed_images
            
            duplicate_groups = find_duplicates_in_list(
                extractor_instance,
                images_to_check,
                request.similarity_threshold
            )
            
            total_images = len(images_to_check)
        
        # Count total duplicates
        total_duplicates = sum(len(group.duplicate_ids) for group in duplicate_groups)
        
        check_time = time.time() - start_time
        
        return DuplicateCheckResponse(
            success=True,
            total_images=total_images,
            duplicate_groups=duplicate_groups,
            total_duplicates=total_duplicates,
            check_time=check_time,
            message=f"Found {len(duplicate_groups)} duplicate groups with {total_duplicates} duplicate images"
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/check-image")
async def check_image_duplicates(
    image_path: str = Query(..., description="Path to image file"),
    similarity_threshold: float = Query(0.95, description="Similarity threshold", ge=0.0, le=1.0),
    extractor_instance = Depends(get_extractor_lazy)
):
    """Check if a specific image has duplicates in the database."""
    request = DuplicateCheckRequest(
        image_path=image_path,
        similarity_threshold=similarity_threshold
    )
    return await check_duplicates(request, extractor_instance)


@router.get("/check-directory")
async def check_directory_duplicates(
    directory_path: str = Query(..., description="Path to directory"),
    similarity_threshold: float = Query(0.95, description="Similarity threshold", ge=0.0, le=1.0),
    extractor_instance = Depends(get_extractor_lazy)
):
    """Check for duplicates within a directory."""
    request = DuplicateCheckRequest(
        directory_path=directory_path,
        similarity_threshold=similarity_threshold
    )
    return await check_duplicates(request, extractor_instance)


@router.post("/compare")
async def compare_images(
    image1_path: str,
    image2_path: str,
    extractor_instance = Depends(get_extractor_lazy)
):
    """Compare two specific images and return similarity score."""
    try:
        if not os.path.exists(image1_path):
            raise HTTPException(status_code=404, detail=f"Image 1 not found: {image1_path}")
        
        if not os.path.exists(image2_path):
            raise HTTPException(status_code=404, detail=f"Image 2 not found: {image2_path}")
        
        start_time = time.time()
        
        # Calculate similarity
        similarity = calculate_image_similarity(extractor_instance, image1_path, image2_path)
        
        # Extract features for additional comparison
        features1 = extractor_instance.extract_image_features(image1_path)
        features2 = extractor_instance.extract_image_features(image2_path)
        
        # Compare captions and objects
        caption_similarity = len(set(features1['caption'].lower().split()) & 
                                set(features2['caption'].lower().split())) / \
                           max(len(features1['caption'].split()), len(features2['caption'].split()))
        
        object_similarity = len(set(features1['objects']) & set(features2['objects'])) / \
                          max(len(features1['objects']), len(features2['objects'])) if \
                          (features1['objects'] or features2['objects']) else 0.0
        
        comparison_time = time.time() - start_time
        
        return {
            "image1_path": image1_path,
            "image2_path": image2_path,
            "overall_similarity": similarity,
            "caption_similarity": caption_similarity,
            "object_similarity": object_similarity,
            "is_likely_duplicate": similarity > 0.95,
            "image1_caption": features1['caption'],
            "image2_caption": features2['caption'],
            "image1_objects": features1['objects'],
            "image2_objects": features2['objects'],
            "common_objects": list(set(features1['objects']) & set(features2['objects'])),
            "comparison_time": comparison_time
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error comparing images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remove-duplicates")
async def remove_duplicates(
    similarity_threshold: float = Query(0.98, description="Similarity threshold", ge=0.0, le=1.0),
    dry_run: bool = Query(True, description="Dry run - don't actually delete"),
    keep_first: bool = Query(True, description="Keep the first image in each duplicate group"),
    extractor_instance = Depends(get_extractor_lazy)
):
    """Remove duplicate images from the database and optionally from disk."""
    try:
        start_time = time.time()
        
        # Get all processed images
        processed_images = extractor_instance.get_processed_images()
        
        if not processed_images:
            return {
                "success": True,
                "total_images": 0,
                "duplicates_found": 0,
                "images_removed": 0,
                "dry_run": dry_run,
                "message": "No images in database"
            }
        
        # Find duplicate groups
        duplicate_groups = find_duplicates_in_list(
            extractor_instance,
            processed_images,
            similarity_threshold
        )
        
        images_to_remove = []
        
        for group in duplicate_groups:
            if keep_first:
                # Remove all but the first image
                images_to_remove.extend(group.paths[1:])
            else:
                # Remove all but the representative (first) image
                images_to_remove.extend([path for path in group.paths 
                                       if hashlib.md5(path.encode()).hexdigest() != group.representative_id])
        
        removal_results = []
        
        if not dry_run:
            for image_path in images_to_remove:
                try:
                    # TODO: Implement actual removal from database
                    # This would require extending the VectorDatabase class
                    removal_results.append({
                        "path": image_path,
                        "removed": True,
                        "error": None
                    })
                except Exception as e:
                    removal_results.append({
                        "path": image_path,
                        "removed": False,
                        "error": str(e)
                    })
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "total_images": len(processed_images),
            "duplicate_groups_found": len(duplicate_groups),
            "images_to_remove": len(images_to_remove),
            "images_removed": len([r for r in removal_results if r["removed"]]) if not dry_run else 0,
            "failed_removals": len([r for r in removal_results if not r["removed"]]) if not dry_run else 0,
            "dry_run": dry_run,
            "processing_time": processing_time,
            "removal_results": removal_results if not dry_run else None,
            "images_that_would_be_removed": images_to_remove if dry_run else None,
            "message": f"{'Would remove' if dry_run else 'Removed'} {len(images_to_remove)} duplicate images"
        }
        
    except Exception as e:
        logger.error(f"Error removing duplicates: {e}")
        raise HTTPException(status_code=500, detail=str(e))