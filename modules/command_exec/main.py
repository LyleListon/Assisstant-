"""
Command Execution Module
Handles system command execution independently
"""

import subprocess
from typing import Dict, Any, Optional, List, Union
import shlex
import os

class CommandExecutor:
    def __init__(self):
        self.supported_actions = {
            "execute": self._execute_command,
            "execute_background": self._execute_background,
            "list_running": self._list_running,
            "terminate": self._terminate_process
        }
        self._running_processes: Dict[str, subprocess.Popen] = {}
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming command execution requests"""
        try:
            action = request.get("action")
            if not action:
                return self._error_response(request.get("id"), "No action specified")
            
            handler = self.supported_actions.get(action)
            if not handler:
                return self._error_response(request.get("id"), f"Unsupported action: {action}")
            
            return handler(request.get("data", {}))
            
        except Exception as e:
            return self._error_response(request.get("id"), str(e))
    
    def _execute_command(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command and wait for completion"""
        command = data.get("command")
        if not command:
            return self._error_response(None, "No command specified")
        
        try:
            # Split command if it's a string
            if isinstance(command, str):
                command = shlex.split(command)
            
            # Execute command and capture output
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True if os.name == 'nt' else False
            )
            
            return self._success_response({
                "stdout": process.stdout,
                "stderr": process.stderr,
                "returncode": process.returncode
            })
        except Exception as e:
            return self._error_response(None, f"Error executing command: {str(e)}")
    
    def _execute_background(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command in the background"""
        command = data.get("command")
        process_id = data.get("process_id", str(len(self._running_processes)))
        
        if not command:
            return self._error_response(None, "No command specified")
        
        try:
            # Split command if it's a string
            if isinstance(command, str):
                command = shlex.split(command)
            
            # Start process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True if os.name == 'nt' else False
            )
            
            self._running_processes[process_id] = process
            
            return self._success_response({
                "process_id": process_id,
                "pid": process.pid
            })
        except Exception as e:
            return self._error_response(None, f"Error starting background process: {str(e)}")
    
    def _list_running(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List all running background processes"""
        running_processes = {}
        
        # Update process statuses
        for pid, process in list(self._running_processes.items()):
            if process.poll() is None:
                running_processes[pid] = {
                    "pid": process.pid,
                    "status": "running"
                }
            else:
                # Process completed, get output
                stdout, stderr = process.communicate()
                running_processes[pid] = {
                    "pid": process.pid,
                    "status": "completed",
                    "returncode": process.returncode,
                    "stdout": stdout,
                    "stderr": stderr
                }
                # Clean up completed process
                del self._running_processes[pid]
        
        return self._success_response({"processes": running_processes})
    
    def _terminate_process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Terminate a running background process"""
        process_id = data.get("process_id")
        if not process_id:
            return self._error_response(None, "No process_id specified")
        
        process = self._running_processes.get(process_id)
        if not process:
            return self._error_response(None, f"Process {process_id} not found")
        
        try:
            process.terminate()
            process.wait(timeout=5)  # Wait up to 5 seconds for termination
            
            stdout, stderr = process.communicate()
            result = {
                "pid": process.pid,
                "returncode": process.returncode,
                "stdout": stdout,
                "stderr": stderr
            }
            
            del self._running_processes[process_id]
            
            return self._success_response(result)
        except subprocess.TimeoutExpired:
            process.kill()  # Force kill if termination times out
            return self._error_response(None, f"Process {process_id} killed after timeout")
        except Exception as e:
            return self._error_response(None, f"Error terminating process: {str(e)}")
    
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
    
    executor = CommandExecutor()
    
    # Example: Execute simple command
    request = {
        "action": "execute",
        "data": {
            "command": "echo Hello, World!"
        }
    }
    
    print("Executing command:")
    print(json.dumps(executor.process_request(request), indent=2))
    
    # Example: Start background process
    bg_request = {
        "action": "execute_background",
        "data": {
            "command": "ping localhost -n 5" if os.name == 'nt' else "ping localhost -c 5",
            "process_id": "ping_test"
        }
    }
    
    print("\nStarting background process:")
    print(json.dumps(executor.process_request(bg_request), indent=2))
    
    # Example: List running processes
    list_request = {
        "action": "list_running",
        "data": {}
    }
    
    print("\nListing running processes:")
    print(json.dumps(executor.process_request(list_request), indent=2))
