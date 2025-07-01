from src.document_processing.core.base import OCRExtractor, Document
import time

class TesseractOCRExtractor(OCRExtractor):
    """
    Example implementation for an OCR extractor using a hypothetical Tesseract wrapper.
    In a real scenario, this would interface with an actual Tesseract library (e.g., pytesseract).
    """
    def __init__(self, tesseract_config: dict | None = None):
        self.config = tesseract_config if tesseract_config else {}
        print(f"TesseractOCRExtractor initialized with config: {self.config}")

    def extract_text(self, document: Document) -> str:
        """
        Simulates text extraction using Tesseract.
        """
        print(f"TesseractOCRExtractor: Starting OCR for document {document.document_id} at {document.document_path}...")

        # Simulate OCR processing time
        time.sleep(0.1) # Short delay for simulation

        # Simulate different outcomes based on document type or content
        if "invoice_document_for_ocr" in document.document_path:
            extracted_text = """
            INVOICE
            Date: 2023-10-26
            Invoice No: INV-001
            To: Client Corp
            Item: Product A, Qty: 2, Price: $50
            Item: Service B, Qty: 1, Price: $100
            Total: $200
            """
            document.raw_text = extracted_text
            print(f"TesseractOCRExtractor: OCR complete for {document.document_id}. Text extracted.")
            return extracted_text
        elif "generic_document_for_ocr" in document.document_path:
            extracted_text = "This is a generic document. It contains various pieces of information. Serial Number: GEN-12345. Date: 2023-11-15."
            document.raw_text = extracted_text
            print(f"TesseractOCRExtractor: OCR complete for {document.document_id}. Text extracted.")
            return extracted_text
        elif document.raw_text and "Dummy PDF content" in document.raw_text : # from PDFDocument dummy content
             extracted_text = f"Extracted text from dummy PDF: {document.raw_text}"
             document.raw_text = extracted_text
             print(f"TesseractOCRExtractor: OCR complete for {document.document_id} (dummy PDF). Text extracted.")
             return extracted_text
        else:
            # Fallback for other cases or if document.raw_text was pre-filled by Document.load_content()
            # and we still want to simulate OCR on it or if it's an image.
            extracted_text = f"Simulated OCR text from {document.document_path}. Content: {document.raw_text[:50]}..."
            document.raw_text = extracted_text # Update document's raw_text
            print(f"TesseractOCRExtractor: OCR complete for {document.document_id}. Text extracted (simulated).")
            return extracted_text

class AzureDocumentIntelligenceExtractor(OCRExtractor):
    """
    Example placeholder for Azure Document Intelligence (formerly Form Recognizer).
    """
    def __init__(self, endpoint: str, api_key: str):
        self.endpoint = endpoint
        self.api_key = api_key # Ensure this is handled securely in real applications
        print(f"AzureDocumentIntelligenceExtractor initialized for endpoint: {self.endpoint}")

    def extract_text(self, document: Document) -> str:
        """
        Simulates text extraction using Azure Document Intelligence.
        """
        print(f"AzureDocumentIntelligenceExtractor: Starting OCR for document {document.document_id} at {document.document_path}...")
        # Simulate API call
        time.sleep(0.1)

        # Example: might return structured data too, but here we focus on raw text
        extracted_text = f"Text extracted by Azure AI from {document.document_path}. Document ID: {document.document_id}."
        if "form_document_for_azure" in document.document_path:
            extracted_text += "\nKey: Name, Value: John Doe\nKey: Address, Value: 123 Main St"

        document.raw_text = extracted_text
        print(f"AzureDocumentIntelligenceExtractor: OCR complete for {document.document_id}.")
        return extracted_text
