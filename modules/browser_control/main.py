"""
Browser Control Module
Handles browser automation and web interactions independently
"""

from typing import Dict, Any, Optional, List
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class BrowserController:
    def __init__(self):
        self.supported_actions = {
            "launch": self._launch_browser,
            "navigate": self._navigate_to_url,
            "click": self._click_element,
            "type": self._type_text,
            "get_text": self._get_element_text,
            "screenshot": self._take_screenshot,
            "close": self._close_browser
        }
        self._driver: Optional[webdriver.Chrome] = None
        self._wait_timeout = 10  # seconds
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming browser control requests"""
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
    
    def _launch_browser(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Launch a new browser instance"""
        if self._driver:
            return self._error_response(None, "Browser already running")
        
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run in headless mode
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self._driver = webdriver.Chrome(options=options)
            self._driver.set_window_size(1920, 1080)
            
            # Navigate to initial URL if provided
            url = data.get("url")
            if url:
                self._driver.get(url)
            
            return self._success_response({"status": "Browser launched successfully"})
        except Exception as e:
            return self._error_response(None, f"Error launching browser: {str(e)}")
    
    def _navigate_to_url(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to a specified URL"""
        if not self._driver:
            return self._error_response(None, "Browser not launched")
        
        url = data.get("url")
        if not url:
            return self._error_response(None, "No URL specified")
        
        try:
            self._driver.get(url)
            return self._success_response({"status": f"Navigated to {url}"})
        except Exception as e:
            return self._error_response(None, f"Error navigating to URL: {str(e)}")
    
    def _click_element(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Click on an element"""
        if not self._driver:
            return self._error_response(None, "Browser not launched")
        
        selector = data.get("selector")
        if not selector:
            return self._error_response(None, "No selector specified")
        
        try:
            element = WebDriverWait(self._driver, self._wait_timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            element.click()
            return self._success_response({"status": f"Clicked element: {selector}"})
        except Exception as e:
            return self._error_response(None, f"Error clicking element: {str(e)}")
    
    def _type_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Type text into an element"""
        if not self._driver:
            return self._error_response(None, "Browser not launched")
        
        selector = data.get("selector")
        text = data.get("text")
        
        if not selector:
            return self._error_response(None, "No selector specified")
        if text is None:
            return self._error_response(None, "No text provided")
        
        try:
            element = WebDriverWait(self._driver, self._wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(text)
            return self._success_response({"status": f"Typed text into element: {selector}"})
        except Exception as e:
            return self._error_response(None, f"Error typing text: {str(e)}")
    
    def _get_element_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get text from an element"""
        if not self._driver:
            return self._error_response(None, "Browser not launched")
        
        selector = data.get("selector")
        if not selector:
            return self._error_response(None, "No selector specified")
        
        try:
            element = WebDriverWait(self._driver, self._wait_timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            text = element.text
            return self._success_response({"text": text})
        except Exception as e:
            return self._error_response(None, f"Error getting element text: {str(e)}")
    
    def _take_screenshot(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot of the current page"""
        if not self._driver:
            return self._error_response(None, "Browser not launched")
        
        path = data.get("path", "screenshot.png")
        try:
            self._driver.save_screenshot(path)
            return self._success_response({"path": path})
        except Exception as e:
            return self._error_response(None, f"Error taking screenshot: {str(e)}")
    
    def _close_browser(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Close the browser instance"""
        if not self._driver:
            return self._error_response(None, "Browser not launched")
        
        try:
            self._driver.quit()
            self._driver = None
            return self._success_response({"status": "Browser closed successfully"})
        except Exception as e:
            return self._error_response(None, f"Error closing browser: {str(e)}")
    
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
    controller = BrowserController()
    
    # Example: Launch browser and navigate to a URL
    launch_request = {
        "action": "launch",
        "data": {
            "url": "https://www.example.com"
        }
    }
    
    print("Launching browser:")
    print(json.dumps(controller.process_request(launch_request), indent=2))
    
    # Example: Click a button
    click_request = {
        "action": "click",
        "data": {
            "selector": "button.submit-button"
        }
    }
    
    print("\nClicking button:")
    print(json.dumps(controller.process_request(click_request), indent=2))
    
    # Example: Close browser
    close_request = {
        "action": "close",
        "data": {}
    }
    
    print("\nClosing browser:")
    print(json.dumps(controller.process_request(close_request), indent=2))
