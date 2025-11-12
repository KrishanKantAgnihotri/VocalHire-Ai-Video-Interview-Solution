"""
File-based storage implementation for interview sessions.
Stores session data as JSON files in the data directory.
"""
import json
import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from ..models.schemas import SessionData, InterviewState, InterviewFeedback


class FileStorage:
    """Handles persistent storage of interview sessions using JSON files"""
    
    def __init__(self, data_dir: str = "./data"):
        """
        Initialize file storage with specified data directory.
        
        Args:
            data_dir: Directory path where session files will be stored
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_session_path(self, session_id: str) -> Path:
        """Get the file path for a given session ID"""
        return self.data_dir / f"session_{session_id}.json"
    
    async def save_session(self, session_data: SessionData) -> bool:
        """
        Save session data to a JSON file.
        
        Args:
            session_data: SessionData object to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            session_data.updated_at = datetime.now()
            file_path = self._get_session_path(session_data.session_id)
            
            # Convert Pydantic model to dict and save as JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data.model_dump(mode='json'), f, indent=2, default=str)
            
            return True
        except Exception as e:
            print(f"Error saving session {session_data.session_id}: {e}")
            return False
    
    async def load_session(self, session_id: str) -> Optional[SessionData]:
        """
        Load session data from a JSON file.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            SessionData object if found, None otherwise
        """
        try:
            file_path = self._get_session_path(session_id)
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return SessionData(**data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session file.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            file_path = self._get_session_path(session_id)
            
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    async def list_sessions(self) -> List[str]:
        """
        List all session IDs in storage.
        
        Returns:
            List of session IDs
        """
        try:
            session_files = self.data_dir.glob("session_*.json")
            session_ids = [f.stem.replace("session_", "") for f in session_files]
            return session_ids
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    async def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists in storage.
        
        Args:
            session_id: ID of the session to check
            
        Returns:
            bool: True if session exists, False otherwise
        """
        file_path = self._get_session_path(session_id)
        return file_path.exists()

