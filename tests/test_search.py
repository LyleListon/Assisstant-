"""
Tests for Search Module
"""

import os
import pytest
from unittest.mock import patch, mock_open
from personal_assistant.modules.search.main import Searcher

@pytest.fixture
def searcher():
    """Create Searcher instance for testing"""
    return Searcher()

@pytest.fixture
def mock_files():
    """Mock file structure for testing"""
    return {
        'test.py': 'def test_function():\n    # TODO: implement this\n    pass\n',
        'main.py': 'print("Hello World")\n# Another line\n',
        'data.txt': 'Some test data\nwith multiple lines\n',
        'config.json': '{"key": "value"}\n'
    }

def test_search_files(searcher):
    """Test searching for files by pattern"""
    mock_walk_data = [
        ('root', [], ['test.py', 'main.py', 'data.txt', 'config.json'])
    ]
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = mock_walk_data
        
        request = {
            "action": "search_files",
            "data": {
                "path": ".",
                "pattern": r"\.py$",
                "recursive": True
            }
        }
        
        response = searcher.process_request(request)
        assert response["success"] is True
        matches = response["data"]["matches"]
        assert len(matches) == 2
        assert any('test.py' in match for match in matches)
        assert any('main.py' in match for match in matches)

def test_search_content(searcher, mock_files):
    """Test searching file contents"""
    mock_walk_data = [
        ('root', [], ['test.py', 'main.py'])
    ]
    
    with patch('os.walk') as mock_walk, \
         patch('builtins.open', mock_open()) as mock_file:
        mock_walk.return_value = mock_walk_data
        # Configure mock file reads
        mock_file.side_effect = lambda file, mode, encoding: mock_open(
            read_data=mock_files[os.path.basename(file)]
        ).return_value
        
        request = {
            "action": "search_content",
            "data": {
                "path": ".",
                "text": "TODO",
                "file_pattern": "*.py",
                "context_lines": 1
            }
        }
        
        response = searcher.process_request(request)
        assert response["success"] is True
        matches = response["data"]["matches"]
        assert len(matches) == 1
        assert "TODO" in matches[0]["content"]
        assert matches[0]["line_number"] == 2  # Line number where TODO appears

def test_find_pattern(searcher, mock_files):
    """Test searching for regex patterns"""
    mock_walk_data = [
        ('root', [], ['test.py', 'main.py'])
    ]
    
    with patch('os.walk') as mock_walk, \
         patch('builtins.open', mock_open()) as mock_file:
        mock_walk.return_value = mock_walk_data
        # Configure mock file reads
        mock_file.side_effect = lambda file, mode, encoding: mock_open(
            read_data=mock_files[os.path.basename(file)]
        ).return_value
        
        request = {
            "action": "find_pattern",
            "data": {
                "path": ".",
                "pattern": r"def\s+\w+\(\)",  # Find function definitions
                "file_pattern": "*.py"
            }
        }
        
        response = searcher.process_request(request)
        assert response["success"] is True
        matches = response["data"]["matches"]
        assert len(matches) == 1
        assert matches[0]["match"] == "def test_function()"

def test_search_by_extension(searcher):
    """Test searching for files by extension"""
    mock_walk_data = [
        ('root', [], ['test.py', 'main.py', 'data.txt', 'config.json'])
    ]
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = mock_walk_data
        
        request = {
            "action": "search_by_extension",
            "data": {
                "path": ".",
                "extension": ".py"
            }
        }
        
        response = searcher.process_request(request)
        assert response["success"] is True
        matches = response["data"]["matches"]
        assert len(matches) == 2
        assert any('test.py' in match for match in matches)
        assert any('main.py' in match for match in matches)

def test_error_handling(searcher):
    """Test error handling"""
    # Test invalid action
    request = {
        "action": "invalid_action",
        "data": {}
    }
    
    response = searcher.process_request(request)
    assert response["success"] is False
    assert "Unsupported action" in response["error"]
    
    # Test missing pattern
    request = {
        "action": "search_files",
        "data": {
            "path": "."
        }
    }
    
    response = searcher.process_request(request)
    assert response["success"] is False
    assert "No search pattern specified" in response["error"]
    
    # Test missing text
    request = {
        "action": "search_content",
        "data": {
            "path": "."
        }
    }
    
    response = searcher.process_request(request)
    assert response["success"] is False
    assert "No search text specified" in response["error"]

def test_non_recursive_search(searcher):
    """Test non-recursive file search"""
    mock_listdir_files = ['test.py', 'main.py', 'data.txt']
    
    with patch('os.listdir') as mock_listdir, \
         patch('os.path.isfile') as mock_isfile:
        mock_listdir.return_value = mock_listdir_files
        mock_isfile.return_value = True
        
        request = {
            "action": "search_files",
            "data": {
                "path": ".",
                "pattern": r"\.py$",
                "recursive": False
            }
        }
        
        response = searcher.process_request(request)
        assert response["success"] is True
        matches = response["data"]["matches"]
        assert len(matches) == 2
        assert any('test.py' in match for match in matches)
        assert any('main.py' in match for match in matches)

def test_pattern_conversion(searcher):
    """Test glob pattern to regex conversion"""
    test_cases = [
        ("*.py", ".*\\.py"),
        ("test?.txt", "test.\\.txt"),
        ("src/*.js", "src/.*\\.js")
    ]
    
    for glob_pattern, expected_regex in test_cases:
        converted = searcher._pattern_to_regex(glob_pattern)
        assert converted == expected_regex

def test_search_with_context(searcher, mock_files):
    """Test content search with different context line settings"""
    mock_walk_data = [
        ('root', [], ['test.py'])
    ]
    
    with patch('os.walk') as mock_walk, \
         patch('builtins.open', mock_open()) as mock_file:
        mock_walk.return_value = mock_walk_data
        mock_file.side_effect = lambda file, mode, encoding: mock_open(
            read_data=mock_files[os.path.basename(file)]
        ).return_value
        
        # Test with no context
        request = {
            "action": "search_content",
            "data": {
                "path": ".",
                "text": "TODO",
                "file_pattern": "*.py",
                "context_lines": 0
            }
        }
        
        response = searcher.process_request(request)
        assert response["success"] is True
        matches = response["data"]["matches"]
        assert len(matches) == 1
        assert len(matches[0]["context"].split('\n')) == 1
        
        # Test with larger context
        request["data"]["context_lines"] = 2
        response = searcher.process_request(request)
        assert response["success"] is True
        matches = response["data"]["matches"]
        assert len(matches) == 1
        assert len(matches[0]["context"].split('\n')) > 1
