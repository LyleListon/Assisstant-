"""
Tests for Command Execution Module
"""

import pytest
from personal_assistant.modules.command_exec.main import CommandExecutor

@pytest.fixture
def command_exec():
    """Create CommandExecutor instance for testing"""
    return CommandExecutor()

def test_execute_command(command_exec):
    """Test executing a simple command"""
    request = {
        "action": "execute",
        "data": {
            "command": "echo Hello World"
        }
    }
    
    response = command_exec.process_request(request)
    assert response["success"] is True
    assert "stdout" in response["data"]
    assert "Hello World" in response["data"]["stdout"]

def test_execute_background(command_exec):
    """Test executing a command in background"""
    request = {
        "action": "execute_background",
        "data": {
            "command": "echo Background Process",
            "process_id": "test_process"
        }
    }
    
    response = command_exec.process_request(request)
    assert response["success"] is True
    assert "process_id" in response["data"]
    assert response["data"]["process_id"] == "test_process"

def test_list_running(command_exec):
    """Test listing running processes"""
    # Start a background process first
    bg_request = {
        "action": "execute_background",
        "data": {
            "command": "echo Test Process",
            "process_id": "list_test"
        }
    }
    command_exec.process_request(bg_request)
    
    # List running processes
    request = {
        "action": "list_running",
        "data": {}
    }
    
    response = command_exec.process_request(request)
    assert response["success"] is True
    assert "processes" in response["data"]

def test_error_handling(command_exec):
    """Test error handling"""
    # Test invalid action
    request = {
        "action": "invalid_action",
        "data": {}
    }
    
    response = command_exec.process_request(request)
    assert response["success"] is False
    assert "error" in response
    
    # Test missing command
    request = {
        "action": "execute",
        "data": {}
    }
    
    response = command_exec.process_request(request)
    assert response["success"] is False
    assert "error" in response

def test_terminate_process(command_exec):
    """Test terminating a process"""
    # Start a background process
    bg_request = {
        "action": "execute_background",
        "data": {
            "command": "echo Termination Test",
            "process_id": "term_test"
        }
    }
    command_exec.process_request(bg_request)
    
    # Terminate the process
    request = {
        "action": "terminate",
        "data": {
            "process_id": "term_test"
        }
    }
    
    response = command_exec.process_request(request)
    assert response["success"] is True
