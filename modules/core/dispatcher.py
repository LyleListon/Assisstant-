"""
Core Dispatcher Module
Handles routing of requests between independent modules
"""

import json
import uuid
from typing import Dict, Any, Optional, Callable, Protocol

class MessageHandler(Protocol):
    """Protocol for message handlers"""
    def __call__(self, request: Dict[str, Any]) -> Dict[str, Any]: ...

class Dispatcher:
    def __init__(self):
        self._modules: Dict[str, MessageHandler] = {}
        self._response_handlers: Dict[str, MessageHandler] = {}
    
    def register_module(self, module_name: str, handler: MessageHandler) -> None:
        """Register a module's message handler"""
        self._modules[module_name] = handler
    
    def create_request(self, module: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a properly formatted request message"""
        return {
            "module": module,
            "action": action,
            "data": data,
            "id": str(uuid.uuid4())
        }
    
    def route_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route a request to the appropriate module"""
        try:
            module = request.get("module")
            if not module:
                return self._error_response(request, "No module specified")
            
            handler = self._modules.get(module)
            if not handler:
                return self._error_response(request, f"Module {module} not found")
            
            return handler(request)
            
        except Exception as e:
            return self._error_response(request, str(e))
    
    def _error_response(self, request: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create an error response"""
        return {
            "success": False,
            "data": None,
            "error": error,
            "id": request.get("id", "unknown")
        }

    def _success_response(self, request: Dict[str, Any], data: Any) -> Dict[str, Any]:
        """Create a success response"""
        return {
            "success": True,
            "data": data,
            "error": None,
            "id": request.get("id")
        }

# Example usage:
if __name__ == "__main__":
    # Create dispatcher
    dispatcher = Dispatcher()
    
    # Example module handler
    def file_ops_handler(request: Dict[str, Any]) -> Dict[str, Any]:
        """Example handler for file operations"""
        action = request.get("action")
        if action == "read":
            # Simulate reading a file
            return {
                "success": True,
                "data": "File contents would go here",
                "error": None,
                "id": request.get("id")
            }
        return {
            "success": False,
            "data": None,
            "error": f"Unknown action: {action}",
            "id": request.get("id")
        }
    
    # Register module
    dispatcher.register_module("file_ops", file_ops_handler)
    
    # Create and route a request
    request = dispatcher.create_request(
        module="file_ops",
        action="read",
        data={"path": "example.txt"}
    )
    
    response = dispatcher.route_request(request)
    print(json.dumps(response, indent=2))
