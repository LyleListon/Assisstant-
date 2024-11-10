"""
Receipt Organizer Module
Handles email receipt collection, processing, and organization
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import os
import re
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class Receipt:
    """Data class for receipt information"""
    date: datetime
    vendor: str
    amount: float
    source_email: str
    file_path: str
    receipt_type: str  # 'email' or 'attachment'
    currency: str = 'USD'
    categories: List[str] = field(default_factory=list)

class ReceiptOrganizer:
    def __init__(self, base_path: str = "data/receipts"):
        self.base_path = Path(base_path)
        self.supported_actions = {
            "collect_receipts": self._collect_receipts,
            "process_receipt": self._process_receipt,
            "search_receipts": self._search_receipts,
            "generate_report": self._generate_report
        }
        
        # Ensure base directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Common receipt patterns
        self.amount_patterns = [
            r'\$\s*\d+(?:\.\d{2})?',  # $XX.XX
            r'Total:\s*\$?\s*\d+(?:\.\d{2})?',  # Total: $XX.XX
            r'Amount:\s*\$?\s*\d+(?:\.\d{2})?'  # Amount: $XX.XX
        ]
        
        # Common vendor patterns
        self.vendor_patterns = [
            r'From:\s*([\w\s]+)',
            r'Merchant:\s*([\w\s]+)',
            r'Store:\s*([\w\s]+)'
        ]
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming receipt organization requests"""
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
    
    def _collect_receipts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect receipts from email"""
        email_provider = data.get("email_provider", "gmail")
        search_terms = data.get("search_terms", ["receipt", "order confirmation", "invoice"])
        date_range = data.get("date_range", {"start": None, "end": None})
        
        try:
            # TODO: Implement email collection logic using browser_control module
            return self._success_response({
                "status": "Receipt collection initiated",
                "search_terms": search_terms,
                "date_range": date_range
            })
        except Exception as e:
            return self._error_response(None, f"Error collecting receipts: {str(e)}")
    
    def _process_receipt(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single receipt"""
        email_content: str = data.get("email_content", "")
        attachments: List[str] = data.get("attachments", [])
        date = data.get("date")
        
        if not email_content and not attachments:
            return self._error_response(None, "No receipt content provided")
        
        try:
            # Extract receipt information
            receipt_info = self._extract_receipt_info(email_content)
            
            # Generate file path
            file_path = self._generate_file_path(receipt_info)
            
            # Save receipt
            # TODO: Implement file saving logic using file_ops module
            
            return self._success_response({
                "receipt_info": receipt_info,
                "file_path": str(file_path)
            })
        except Exception as e:
            return self._error_response(None, f"Error processing receipt: {str(e)}")
    
    def _search_receipts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Search through organized receipts"""
        query = data.get("query", {})
        date_range = query.get("date_range", {})
        vendor = query.get("vendor")
        amount_range = query.get("amount_range", {})
        
        try:
            # TODO: Implement search logic using search module
            return self._success_response({
                "status": "Search initiated",
                "query": query
            })
        except Exception as e:
            return self._error_response(None, f"Error searching receipts: {str(e)}")
    
    def _generate_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate expense report"""
        report_type = data.get("report_type", "monthly")
        date_range = data.get("date_range", {})
        categories = data.get("categories", [])
        
        try:
            # TODO: Implement report generation logic
            return self._success_response({
                "status": "Report generation initiated",
                "report_type": report_type,
                "date_range": date_range
            })
        except Exception as e:
            return self._error_response(None, f"Error generating report: {str(e)}")
    
    def _extract_receipt_info(self, content: str) -> Dict[str, Any]:
        """Extract key information from receipt content"""
        # Extract amount
        amount: Optional[float] = None
        for pattern in self.amount_patterns:
            match = re.search(pattern, content)
            if match:
                amount_str = re.sub(r'[^\d.]', '', match.group())
                amount = float(amount_str)
                break
        
        # Extract vendor
        vendor: Optional[str] = None
        for pattern in self.vendor_patterns:
            match = re.search(pattern, content)
            if match:
                vendor = match.group(1).strip()
                break
        
        # Extract date (assuming it's provided in the email metadata)
        date = datetime.now()  # Placeholder
        
        return {
            "date": date,
            "vendor": vendor or "Unknown",
            "amount": amount or 0.0,
            "currency": "USD"  # Default currency
        }
    
    def _generate_file_path(self, receipt_info: Dict[str, Any]) -> Path:
        """Generate organized file path for receipt"""
        date = receipt_info["date"]
        vendor = receipt_info["vendor"] or "Unknown_Vendor"
        amount = receipt_info["amount"] or 0.0
        
        # Create year/month directory structure
        year_dir = self.base_path / str(date.year)
        month_dir = year_dir / f"{date.month:02d}"
        month_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename: YYYY-MM-DD_Vendor_Amount.pdf
        filename = f"{date.strftime('%Y-%m-%d')}_{vendor}_{amount:.2f}.pdf"
        return month_dir / filename
    
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
    
    organizer = ReceiptOrganizer()
    
    # Example: Collect receipts
    collect_request = {
        "action": "collect_receipts",
        "data": {
            "email_provider": "gmail",
            "search_terms": ["receipt", "order confirmation"],
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-03-14"
            }
        }
    }
    
    print("Collecting receipts:")
    print(json.dumps(organizer.process_request(collect_request), indent=2))
