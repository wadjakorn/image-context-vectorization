"""
Directory validation and security utilities for external directories.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DirectoryInfo:
    """Information about a directory"""
    id: str
    path: str
    name: str
    accessible: bool
    exists: bool
    readable: bool
    last_checked: str
    image_count: Optional[int] = None
    supported_image_count: Optional[int] = None
    error_message: Optional[str] = None

class DirectoryValidator:
    """Validates and manages external directories safely"""
    
    # Forbidden paths for security
    FORBIDDEN_PATHS = {
        '/', '/bin', '/boot', '/dev', '/etc', '/lib', '/lib64', '/proc', '/root', 
        '/run', '/sbin', '/sys', '/tmp', '/usr', '/var', '/home', '/System',
        '/Applications', '/Library', '/private', '/usr/local', '/opt'
    }
    
    # Forbidden path patterns
    FORBIDDEN_PATTERNS = {
        'passwd', 'shadow', 'hosts', 'ssh', 'ssl', 'cert', 'key', 'private',
        'config', 'secret', 'token', 'credential'
    }
    
    def __init__(self, supported_formats: List[str] = None):
        """Initialize with supported image formats"""
        self.supported_formats = supported_formats or ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp']
    
    def generate_directory_id(self, path: str) -> str:
        """Generate a unique ID for a directory path"""
        normalized_path = os.path.normpath(os.path.abspath(path))
        return hashlib.md5(normalized_path.encode()).hexdigest()[:12]
    
    def is_safe_path(self, path: str) -> Tuple[bool, str]:
        """Check if a path is safe to access"""
        try:
            # Normalize and resolve the path
            normalized_path = os.path.normpath(os.path.abspath(path))
            resolved_path = os.path.realpath(normalized_path)
            
            # Check if it's a forbidden system path
            if resolved_path in self.FORBIDDEN_PATHS:
                return False, f"Access to system directory '{resolved_path}' is forbidden"
            
            # Check if path starts with forbidden directories
            for forbidden in self.FORBIDDEN_PATHS:
                if resolved_path.startswith(forbidden + os.sep) or resolved_path == forbidden:
                    return False, f"Access to path under '{forbidden}' is forbidden"
            
            # Check for forbidden patterns in path
            path_lower = resolved_path.lower()
            for pattern in self.FORBIDDEN_PATTERNS:
                if pattern in path_lower:
                    return False, f"Path contains forbidden pattern: '{pattern}'"
            
            # Check for directory traversal attempts
            if '..' in normalized_path or '~' in normalized_path:
                return False, "Path traversal attempts are not allowed"
            
            return True, "Path is safe"
            
        except Exception as e:
            return False, f"Error validating path: {str(e)}"
    
    def validate_directory(self, path: str) -> DirectoryInfo:
        """Validate a single directory and return its info"""
        try:
            # Generate directory ID
            dir_id = self.generate_directory_id(path)
            
            # Get directory name
            dir_name = os.path.basename(path) or "Root"
            
            # Check if path is safe
            is_safe, safety_message = self.is_safe_path(path)
            if not is_safe:
                return DirectoryInfo(
                    id=dir_id,
                    path=path,
                    name=dir_name,
                    accessible=False,
                    exists=False,
                    readable=False,
                    last_checked=datetime.now().isoformat(),
                    error_message=safety_message
                )
            
            # Check if directory exists
            path_obj = Path(path)
            exists = path_obj.exists()
            
            if not exists:
                return DirectoryInfo(
                    id=dir_id,
                    path=path,
                    name=dir_name,
                    accessible=False,
                    exists=False,
                    readable=False,
                    last_checked=datetime.now().isoformat(),
                    error_message="Directory does not exist"
                )
            
            # Check if it's actually a directory
            if not path_obj.is_dir():
                return DirectoryInfo(
                    id=dir_id,
                    path=path,
                    name=dir_name,
                    accessible=False,
                    exists=exists,
                    readable=False,
                    last_checked=datetime.now().isoformat(),
                    error_message="Path is not a directory"
                )
            
            # Check if directory is readable
            readable = os.access(path, os.R_OK)
            
            # Count images if accessible
            image_count = None
            supported_image_count = None
            
            if readable:
                try:
                    image_count, supported_image_count = self._count_images(path)
                except Exception as e:
                    return DirectoryInfo(
                        id=dir_id,
                        path=path,
                        name=dir_name,
                        accessible=False,
                        exists=exists,
                        readable=False,
                        last_checked=datetime.now().isoformat(),
                        error_message=f"Error counting images: {str(e)}"
                    )
            
            return DirectoryInfo(
                id=dir_id,
                path=path,
                name=dir_name,
                accessible=readable,
                exists=exists,
                readable=readable,
                last_checked=datetime.now().isoformat(),
                image_count=image_count,
                supported_image_count=supported_image_count,
                error_message=None if readable else "Directory is not readable"
            )
            
        except Exception as e:
            return DirectoryInfo(
                id=self.generate_directory_id(path),
                path=path,
                name=os.path.basename(path) or "Unknown",
                accessible=False,
                exists=False,
                readable=False,
                last_checked=datetime.now().isoformat(),
                error_message=f"Validation error: {str(e)}"
            )
    
    def _count_images(self, path: str) -> Tuple[int, int]:
        """Count total images and supported images in directory"""
        path_obj = Path(path)
        
        total_images = 0
        supported_images = 0
        
        # Common image extensions (case-insensitive)
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg'}
        
        try:
            for item in path_obj.iterdir():
                if item.is_file():
                    suffix = item.suffix.lower()
                    if suffix in image_extensions:
                        total_images += 1
                        if suffix in [fmt.lower() for fmt in self.supported_formats]:
                            supported_images += 1
        except PermissionError:
            # If we can't read the directory, return 0 counts
            return 0, 0
        
        return total_images, supported_images
    
    def validate_directories(self, paths: List[str]) -> List[DirectoryInfo]:
        """Validate multiple directories"""
        return [self.validate_directory(path) for path in paths]
    
    def get_accessible_directories(self, paths: List[str]) -> List[DirectoryInfo]:
        """Get only accessible directories from a list of paths"""
        return [info for info in self.validate_directories(paths) if info.accessible]
    
    def scan_directory_safe(self, path: str, recursive: bool = True, max_depth: int = 3, 
                          follow_symlinks: bool = False) -> List[str]:
        """Safely scan directory for image files"""
        # First validate the directory
        dir_info = self.validate_directory(path)
        
        if not dir_info.accessible:
            raise ValueError(f"Directory is not accessible: {dir_info.error_message}")
        
        return self._scan_directory_recursive(path, recursive, max_depth, follow_symlinks, 0)
    
    def _scan_directory_recursive(self, path: str, recursive: bool, max_depth: int, 
                                follow_symlinks: bool, current_depth: int) -> List[str]:
        """Recursively scan directory for image files"""
        image_files = []
        
        try:
            path_obj = Path(path)
            
            for item in path_obj.iterdir():
                try:
                    # Skip symlinks if not following them
                    if item.is_symlink() and not follow_symlinks:
                        continue
                    
                    if item.is_file():
                        # Check if it's a supported image format
                        if item.suffix.lower() in [fmt.lower() for fmt in self.supported_formats]:
                            image_files.append(str(item))
                    
                    elif item.is_dir() and recursive and current_depth < max_depth:
                        # Recursively scan subdirectory
                        sub_files = self._scan_directory_recursive(
                            str(item), recursive, max_depth, follow_symlinks, current_depth + 1
                        )
                        image_files.extend(sub_files)
                
                except PermissionError:
                    # Skip files/directories we can't access
                    continue
                except Exception:
                    # Skip any other errors and continue
                    continue
        
        except PermissionError:
            # Can't read the directory
            pass
        
        return image_files