"""
File Operations Module
Handles all file-related operations independently
"""

import os
import json
from typing import Dict, Any, Optional

class FileOps:
    def __init__(self):
        self.supported_actions = {
            "read": self._read_file,
            "write": self._write_file,
            "list": self._list_files,
            "exists": self._file_exists
        }
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming file operation requests"""
        try:
            action = request.get("action")
            request_id = request.get("id")
            if not action:
                return self._error_response(request_id if isinstance(request_id, str) else None, "No action specified")
            
            handler = self.supported_actions.get(action)
            if not handler:
                return self._error_response(request_id if isinstance(request_id, str) else None, f"Unsupported action: {action}")
            
            return handler(request.get("data", {}))
            
        except Exception as e:
            return self._error_response(None, str(e))
    
    def _read_file(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Read file contents"""
        path = data.get("path")
        if not path:
            return self._error_response(None, "No path specified")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._success_response({"content": content})
        except Exception as e:
            return self._error_response(None, f"Error reading file: {str(e)}")
    
    def _write_file(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Write content to file"""
        path = data.get("path")
        content = data.get("content")
        
        if not path:
            return self._error_response(None, "No path specified")
        if content is None:
            return self._error_response(None, "No content provided")
        
        try:
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return self._success_response({"path": path})
        except Exception as e:
            return self._error_response(None, f"Error writing file: {str(e)}")
    
    def _list_files(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List files in directory"""
        path = data.get("path", ".")
        recursive = data.get("recursive", False)
        
        try:
            if recursive:
                files = []
                for root, _, filenames in os.walk(path):
                    for filename in filenames:
                        files.append(os.path.join(root, filename))
            else:
                files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            
            return self._success_response({"files": files})
        except Exception as e:
            return self._error_response(None, f"Error listing files: {str(e)}")
    
    def _file_exists(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if file exists"""
        path = data.get("path")
        if not path:
            return self._error_response(None, "No path specified")
        
        exists = os.path.exists(path)
        return self._success_response({"exists": exists})
    
    def _error_response(self, request_id: Optional[str], error: str) -> Dict[str, Any]:
        """Create an error response"""
        return {
            "success": False,
            "data": None,
            "error": error,
            "id": request_id
        }
    
    def _success_response(self, data: Any) -> Dict[str, Any]:
        """Create a success response"""
        return {
            "success": True,
            "data": data,
            "error": None
        }

# Example usage:
if __name__ == "__main__":
    file_ops = FileOps()
    
    # Example: Write a file
    write_request = {
        "action": "write",
        "data": {
            "path": "test.txt",
            "content": "Hello, World!"
        }
    }
    
    print("Writing file:")
    print(json.dumps(file_ops.process_request(write_request), indent=2))
    
    # Example: Read the file
    read_request = {
        "action": "read",
        "data": {
            "path": "test.txt"
        }
    }
    
    print("\nReading file:")
    print(json.dumps(file_ops.process_request(read_request), indent=2))
