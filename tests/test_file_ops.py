"""
Tests for File Operations Module
"""

import os
import pytest
from personal_assistant.modules.file_ops.main import FileOps

@pytest.fixture
def file_ops():
    """Create FileOps instance for testing"""
    return FileOps()

@pytest.fixture
def test_file(tmp_path):
    """Create a temporary test file"""
    file_path = tmp_path / "test.txt"
    content = "Test content\nSecond line\nThird line"
    file_path.write_text(content)
    return str(file_path)

def test_read_file(file_ops, test_file):
    """Test reading a file"""
    request = {
        "action": "read",
        "data": {
            "path": test_file
        }
    }
    
    response = file_ops.process_request(request)
    assert response["success"] is True
    assert "content" in response["data"]
    assert "Test content" in response["data"]["content"]

def test_write_file(file_ops, tmp_path):
    """Test writing to a file"""
    file_path = str(tmp_path / "write_test.txt")
    content = "New content"
    
    request = {
        "action": "write",
        "data": {
            "path": file_path,
            "content": content
        }
    }
    
    response = file_ops.process_request(request)
    assert response["success"] is True
    assert os.path.exists(file_path)
    with open(file_path, 'r') as f:
        assert f.read() == content

def test_list_files(file_ops, tmp_path):
    """Test listing files"""
    # Create some test files
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "file2.txt").write_text("content2")
    
    request = {
        "action": "list",
        "data": {
            "path": str(tmp_path)
        }
    }
    
    response = file_ops.process_request(request)
    assert response["success"] is True
    assert len(response["data"]["files"]) == 2
    assert any("file1.txt" in f for f in response["data"]["files"])
    assert any("file2.txt" in f for f in response["data"]["files"])

def test_file_exists(file_ops, test_file):
    """Test checking if file exists"""
    request = {
        "action": "exists",
        "data": {
            "path": test_file
        }
    }
    
    response = file_ops.process_request(request)
    assert response["success"] is True
    assert response["data"]["exists"] is True

def test_error_handling(file_ops):
    """Test error handling"""
    # Test invalid action
    request = {
        "action": "invalid_action",
        "data": {}
    }
    
    response = file_ops.process_request(request)
    assert response["success"] is False
    assert "error" in response
    
    # Test missing path
    request = {
        "action": "read",
        "data": {}
    }
    
    response = file_ops.process_request(request)
    assert response["success"] is False
    assert "error" in response
