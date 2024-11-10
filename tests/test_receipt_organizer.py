"""
Tests for the Receipt Organizer module
"""

import pytest
from datetime import datetime
from pathlib import Path
import sys
from os.path import dirname, abspath
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from modules.receipt_organizer import ReceiptOrganizer, Receipt

@pytest.fixture
def organizer(tmp_path):
    """Create a ReceiptOrganizer instance with a temporary base path"""
    return ReceiptOrganizer(base_path=str(tmp_path))

@pytest.fixture
def sample_receipt_email():
    """Sample email content containing receipt information"""
    return """
    From: Amazon.com
    Date: March 14, 2024
    Subject: Your Amazon.com order confirmation
    
    Order Total: $29.99
    
    Thank you for your purchase!
    """

def test_receipt_organizer_initialization(organizer):
    """Test ReceiptOrganizer initialization"""
    assert organizer.base_path.exists()
    assert organizer.base_path.is_dir()

def test_process_receipt(organizer, sample_receipt_email):
    """Test processing a receipt from email content"""
    request = {
        "action": "process_receipt",
        "data": {
            "email_content": sample_receipt_email,
            "date": datetime.now().isoformat()
        }
    }
    
    response = organizer.process_request(request)
    assert response["success"]
    assert "receipt_info" in response["data"]
    
    receipt_info = response["data"]["receipt_info"]
    assert receipt_info["vendor"] == "Amazon.com"
    assert receipt_info["amount"] == 29.99

def test_extract_receipt_info(organizer, sample_receipt_email):
    """Test extraction of receipt information from email content"""
    info = organizer._extract_receipt_info(sample_receipt_email)
    
    assert isinstance(info, dict)
    assert info["vendor"] == "Amazon.com"
    assert info["amount"] == 29.99
    assert info["currency"] == "USD"
    assert isinstance(info["date"], datetime)

def test_generate_file_path(organizer):
    """Test generation of organized file paths"""
    receipt_info = {
        "date": datetime(2024, 3, 14),
        "vendor": "Amazon",
        "amount": 29.99
    }
    
    file_path = organizer._generate_file_path(receipt_info)
    assert isinstance(file_path, Path)
    assert "2024" in str(file_path)
    assert "03" in str(file_path)
    assert "Amazon" in str(file_path)
    assert "29.99" in str(file_path)

def test_search_receipts(organizer):
    """Test receipt search functionality"""
    request = {
        "action": "search_receipts",
        "data": {
            "query": {
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-03-14"
                },
                "vendor": "Amazon",
                "amount_range": {
                    "min": 20,
                    "max": 50
                }
            }
        }
    }
    
    response = organizer.process_request(request)
    assert response["success"]
    assert "query" in response["data"]

def test_generate_report(organizer):
    """Test report generation"""
    request = {
        "action": "generate_report",
        "data": {
            "report_type": "monthly",
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-03-14"
            },
            "categories": ["electronics", "books"]
        }
    }
    
    response = organizer.process_request(request)
    assert response["success"]
    assert response["data"]["report_type"] == "monthly"

def test_invalid_action(organizer):
    """Test handling of invalid actions"""
    request = {
        "action": "invalid_action",
        "data": {}
    }
    
    response = organizer.process_request(request)
    assert not response["success"]
    assert "Unsupported action" in response["error"]

def test_missing_action(organizer):
    """Test handling of missing action"""
    request = {
        "data": {}
    }
    
    response = organizer.process_request(request)
    assert not response["success"]
    assert "No action specified" in response["error"]
