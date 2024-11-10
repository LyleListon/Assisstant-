"""
Search Module
Handles file and content searching operations independently
"""

import os
import re
from typing import Dict, Any, Optional, List, Pattern
from concurrent.futures import ThreadPoolExecutor, as_completed

class Searcher:
    def __init__(self):
        self.supported_actions = {
            "search_files": self._search_files,
            "search_content": self._search_content,
            "find_pattern": self._find_pattern,
            "search_by_extension": self._search_by_extension
        }
        self._max_workers = 4  # Number of parallel search threads
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming search requests"""
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
    
    def _search_files(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files by name pattern"""
        path = data.get("path", ".")
        pattern = data.get("pattern")
        recursive = data.get("recursive", True)
        
        if not pattern:
            return self._error_response(None, "No search pattern specified")
        
        try:
            pattern_regex = re.compile(pattern)
            matches = []
            
            if recursive:
                for root, _, files in os.walk(path):
                    for file in files:
                        if pattern_regex.search(file):
                            matches.append(os.path.join(root, file))
            else:
                matches = [f for f in os.listdir(path) 
                          if os.path.isfile(os.path.join(path, f)) and pattern_regex.search(f)]
            
            return self._success_response({"matches": matches})
        except Exception as e:
            return self._error_response(None, f"Error searching files: {str(e)}")
    
    def _search_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search file contents for text"""
        path = data.get("path", ".")
        text = data.get("text")
        file_pattern = data.get("file_pattern", "*")
        context_lines = data.get("context_lines", 2)
        
        if not text:
            return self._error_response(None, "No search text specified")
        
        try:
            file_regex = re.compile(self._pattern_to_regex(file_pattern))
            text_regex = re.compile(text)
            matches = []
            
            def search_file(file_path: str) -> List[Dict[str, Any]]:
                file_matches = []
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if text_regex.search(line):
                                start = max(0, i - context_lines)
                                end = min(len(lines), i + context_lines + 1)
                                context = {
                                    "file": file_path,
                                    "line_number": i + 1,
                                    "content": line.strip(),
                                    "context": "".join(lines[start:end]).strip()
                                }
                                file_matches.append(context)
                except Exception:
                    pass  # Skip files that can't be read
                return file_matches
            
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                futures = []
                for root, _, files in os.walk(path):
                    for file in files:
                        if file_regex.match(file):
                            file_path = os.path.join(root, file)
                            futures.append(executor.submit(search_file, file_path))
                
                for future in as_completed(futures):
                    matches.extend(future.result())
            
            return self._success_response({"matches": matches})
        except Exception as e:
            return self._error_response(None, f"Error searching content: {str(e)}")
    
    def _find_pattern(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for regex pattern in files"""
        path = data.get("path", ".")
        pattern = data.get("pattern")
        file_pattern = data.get("file_pattern", "*")
        
        if not pattern:
            return self._error_response(None, "No regex pattern specified")
        
        try:
            pattern_regex = re.compile(pattern)
            file_regex = re.compile(self._pattern_to_regex(file_pattern))
            matches = []
            
            def search_file(file_path: str) -> List[Dict[str, Any]]:
                file_matches = []
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for match in pattern_regex.finditer(content):
                            context = {
                                "file": file_path,
                                "start": match.start(),
                                "end": match.end(),
                                "match": match.group(),
                                "groups": match.groups()
                            }
                            file_matches.append(context)
                except Exception:
                    pass  # Skip files that can't be read
                return file_matches
            
            with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                futures = []
                for root, _, files in os.walk(path):
                    for file in files:
                        if file_regex.match(file):
                            file_path = os.path.join(root, file)
                            futures.append(executor.submit(search_file, file_path))
                
                for future in as_completed(futures):
                    matches.extend(future.result())
            
            return self._success_response({"matches": matches})
        except Exception as e:
            return self._error_response(None, f"Error finding pattern: {str(e)}")
    
    def _search_by_extension(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files by extension"""
        path = data.get("path", ".")
        extension = data.get("extension")
        
        if not extension:
            return self._error_response(None, "No file extension specified")
        
        try:
            if not extension.startswith("."):
                extension = f".{extension}"
            
            matches = []
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(extension):
                        matches.append(os.path.join(root, file))
            
            return self._success_response({"matches": matches})
        except Exception as e:
            return self._error_response(None, f"Error searching by extension: {str(e)}")
    
    def _pattern_to_regex(self, pattern: str) -> str:
        """Convert glob pattern to regex pattern"""
        return pattern.replace(".", "\\.").replace("*", ".*").replace("?", ".")
    
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
    import json
    searcher = Searcher()
    
    # Example: Search for Python files
    file_request = {
        "action": "search_files",
        "data": {
            "path": ".",
            "pattern": r"\.py$",
            "recursive": True
        }
    }
    
    print("Searching for Python files:")
    print(json.dumps(searcher.process_request(file_request), indent=2))
    
    # Example: Search for TODO comments
    content_request = {
        "action": "search_content",
        "data": {
            "path": ".",
            "text": "TODO:",
            "file_pattern": "*.py",
            "context_lines": 2
        }
    }
    
    print("\nSearching for TODO comments:")
    print(json.dumps(searcher.process_request(content_request), indent=2))
