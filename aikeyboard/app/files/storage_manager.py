"""
User-isolated file storage manager
"""
from pathlib import Path
import shutil
import uuid
from typing import Optional
import os

from app.config import UPLOAD_DIR


class StorageManager:
    """Manages user-isolated file storage"""
    
    @staticmethod
    def get_user_directory(user_id: int) -> Path:
        """
        Get user-specific storage directory
        
        Args:
            user_id: User ID
            
        Returns:
            Path to user directory
        """
        user_dir = UPLOAD_DIR / f"user_{user_id}"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    
    @staticmethod
    def get_user_files_directory(user_id: int) -> Path:
        """
        Get user-specific files directory
        
        Args:
            user_id: User ID
            
        Returns:
            Path to user files directory
        """
        files_dir = StorageManager.get_user_directory(user_id) / "files"
        files_dir.mkdir(parents=True, exist_ok=True)
        return files_dir
    
    @staticmethod
    def get_user_kb_directory(user_id: int) -> Path:
        """
        Get user-specific knowledge base directory
        
        Args:
            user_id: User ID
            
        Returns:
            Path to user knowledge base directory
        """
        kb_dir = StorageManager.get_user_directory(user_id) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        return kb_dir
    
    @staticmethod
    def save_uploaded_file(user_id: int, file_content, original_filename: str) -> tuple[str, str]:
        """
        Save an uploaded file to user's directory
        
        Args:
            user_id: User ID
            file_content: File content (file-like object)
            original_filename: Original filename
            
        Returns:
            Tuple of (file_id, file_path)
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Get user files directory
        files_dir = StorageManager.get_user_files_directory(user_id)
        
        # Create file path
        file_extension = Path(original_filename).suffix
        file_name = f"{file_id}{file_extension}"
        file_path = files_dir / file_name
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_content, buffer)
        
        return file_id, str(file_path)
    
    @staticmethod
    def delete_file(user_id: int, file_path: str) -> bool:
        """
        Delete a file from user's directory
        
        Args:
            user_id: User ID
            file_path: Path to file
            
        Returns:
            True if deleted successfully
        """
        try:
            # Verify file is in user's directory
            user_dir = StorageManager.get_user_directory(user_id)
            file_path_obj = Path(file_path)
            
            # Security check: ensure file is within user's directory
            if not str(file_path_obj).startswith(str(user_dir)):
                return False
            
            # Delete file
            if file_path_obj.exists():
                file_path_obj.unlink()
                return True
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def get_file_path(user_id: int, file_id: str, file_extension: str) -> Optional[Path]:
        """
        Get file path for a user's file
        
        Args:
            user_id: User ID
            file_id: File ID
            file_extension: File extension
            
        Returns:
            Path to file if exists, None otherwise
        """
        files_dir = StorageManager.get_user_files_directory(user_id)
        file_path = files_dir / f"{file_id}{file_extension}"
        
        if file_path.exists():
            return file_path
        
        return None
    
    @staticmethod
    def delete_user_data(user_id: int) -> bool:
        """
        Delete all data for a user
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted successfully
        """
        try:
            user_dir = StorageManager.get_user_directory(user_id)
            if user_dir.exists():
                shutil.rmtree(user_dir)
                return True
            return False
        except Exception:
            return False
