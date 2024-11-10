"""
Tests for Browser Control Module
"""

import pytest
from unittest.mock import Mock, patch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from personal_assistant.modules.browser_control.main import BrowserController

@pytest.fixture
def browser_controller():
    """Create BrowserController instance for testing"""
    return BrowserController()

@pytest.fixture
def mock_driver():
    """Create a mock Chrome driver"""
    with patch('selenium.webdriver.Chrome') as mock_chrome:
        driver = mock_chrome.return_value
        driver.page_source = "<html><body><button class='test-button'>Click Me</button></body></html>"
        yield driver

@pytest.fixture
def mock_element():
    """Create a mock element with common attributes"""
    element = Mock()
    element.text = "Test text content"
    return element

@pytest.fixture
def browser_with_mock_driver(browser_controller, mock_driver):
    """Setup browser controller with mock driver"""
    browser_controller._driver = mock_driver
    return browser_controller

def test_launch_browser(browser_controller, mock_driver):
    """Test browser launch functionality"""
    request = {
        "action": "launch",
        "data": {
            "url": "https://example.com"
        }
    }
    
    response = browser_controller.process_request(request)
    assert response["success"] is True
    assert "Browser launched successfully" in response["data"]["status"]
    mock_driver.get.assert_called_once_with("https://example.com")

def test_navigate_to_url(browser_with_mock_driver):
    """Test URL navigation"""
    request = {
        "action": "navigate",
        "data": {
            "url": "https://example.com/page"
        }
    }
    
    response = browser_with_mock_driver.process_request(request)
    assert response["success"] is True
    assert "Navigated to" in response["data"]["status"]
    browser_with_mock_driver._driver.get.assert_called_once_with("https://example.com/page")

def test_click_element(browser_with_mock_driver, mock_element):
    """Test clicking an element"""
    with patch('selenium.webdriver.support.wait.WebDriverWait', autospec=True) as mock_wait_class, \
         patch('selenium.webdriver.support.expected_conditions.element_to_be_clickable', autospec=True) as mock_ec_click:
        # Configure WebDriverWait
        wait_instance = mock_wait_class.return_value
        wait_instance.until.return_value = mock_element
        
        # Configure expected_conditions
        mock_ec_click.return_value = lambda driver: mock_element
        
        request = {
            "action": "click",
            "data": {
                "selector": "button.test-button"
            }
        }
        
        response = browser_with_mock_driver.process_request(request)
        assert response["success"] is True
        assert "Clicked element" in response["data"]["status"]
        mock_element.click.assert_called_once()

def test_type_text(browser_with_mock_driver, mock_element):
    """Test typing text into an element"""
    with patch('selenium.webdriver.support.wait.WebDriverWait', autospec=True) as mock_wait_class, \
         patch('selenium.webdriver.support.expected_conditions.presence_of_element_located', autospec=True) as mock_ec_present:
        # Configure WebDriverWait
        wait_instance = mock_wait_class.return_value
        wait_instance.until.return_value = mock_element
        
        # Configure expected_conditions
        mock_ec_present.return_value = lambda driver: mock_element
        
        request = {
            "action": "type",
            "data": {
                "selector": "input.test-input",
                "text": "Test text"
            }
        }
        
        response = browser_with_mock_driver.process_request(request)
        assert response["success"] is True
        assert "Typed text into element" in response["data"]["status"]
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once_with("Test text")

def test_get_element_text(browser_with_mock_driver, mock_element):
    """Test getting text from an element"""
    with patch('selenium.webdriver.support.wait.WebDriverWait', autospec=True) as mock_wait_class, \
         patch('selenium.webdriver.support.expected_conditions.presence_of_element_located', autospec=True) as mock_ec_present:
        # Configure WebDriverWait
        wait_instance = mock_wait_class.return_value
        wait_instance.until.return_value = mock_element
        
        # Configure expected_conditions
        mock_ec_present.return_value = lambda driver: mock_element
        
        request = {
            "action": "get_text",
            "data": {
                "selector": "div.test-div"
            }
        }
        
        response = browser_with_mock_driver.process_request(request)
        assert response["success"] is True
        assert response["data"]["text"] == "Test text content"

def test_take_screenshot(browser_with_mock_driver, tmp_path):
    """Test taking a screenshot"""
    screenshot_path = str(tmp_path / "test_screenshot.png")
    request = {
        "action": "screenshot",
        "data": {
            "path": screenshot_path
        }
    }
    
    response = browser_with_mock_driver.process_request(request)
    assert response["success"] is True
    assert response["data"]["path"] == screenshot_path
    browser_with_mock_driver._driver.save_screenshot.assert_called_once_with(screenshot_path)

def test_close_browser(browser_with_mock_driver):
    """Test browser closure"""
    # Store reference to mock driver before closing
    mock_driver = browser_with_mock_driver._driver
    
    request = {
        "action": "close",
        "data": {}
    }
    
    response = browser_with_mock_driver.process_request(request)
    assert response["success"] is True
    assert "Browser closed successfully" in response["data"]["status"]
    mock_driver.quit.assert_called_once()
    assert browser_with_mock_driver._driver is None

def test_error_handling(browser_controller):
    """Test error handling"""
    # Test invalid action
    request = {
        "action": "invalid_action",
        "data": {}
    }
    
    response = browser_controller.process_request(request)
    assert response["success"] is False
    assert "Unsupported action" in response["error"]
    
    # Test browser not launched
    request = {
        "action": "click",
        "data": {
            "selector": "button.test-button"
        }
    }
    
    response = browser_controller.process_request(request)
    assert response["success"] is False
    assert "Browser not launched" in response["error"]
    
    # Test missing selector
    browser_controller._driver = Mock()  # Mock a launched browser
    request = {
        "action": "click",
        "data": {}
    }
    
    response = browser_controller.process_request(request)
    assert response["success"] is False
    assert "No selector specified" in response["error"]
