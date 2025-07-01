from src.document_processing.core.base import DocumentClassifier, Document
import re

class InvoiceClassifier(DocumentClassifier):
    """
    Example implementation for classifying invoices.
    """
    def classify(self, document: Document) -> str:
        """
        Classifies the document as 'invoice' if specific keywords are found.
        """
        print(f"InvoiceClassifier: Classifying document {document.document_id}...")
        if not document.raw_text:
            print(f"InvoiceClassifier: No raw text in document {document.document_id} to classify.")
            return "unknown"

        # Simple keyword-based classification
        if "INVOICE" in document.raw_text.upper() or "Invoice No" in document.raw_text:
            document.document_type = "invoice"
            print(f"InvoiceClassifier: Document {document.document_id} classified as 'invoice'.")
            return "invoice"

        document.document_type = "other" # Default if not invoice
        print(f"InvoiceClassifier: Document {document.document_id} classified as 'other' by InvoiceClassifier.")
        return "other"

class GeneralDocumentClassifier(DocumentClassifier):
    """
    A more general classifier that can identify multiple document types
    or act as a fallback.
    """
    def __init__(self, classification_rules: dict | None = None):
        # Rules could be like: {"payslip": ["payslip", "salary slip"], "id_card": ["identity card", "driver license"]}
        self.rules = classification_rules if classification_rules else {}
        print(f"GeneralDocumentClassifier initialized with rules: {list(self.rules.keys())}")

    def classify(self, document: Document) -> str:
        """
        Classifies document based on pre-defined keywords for various types.
        """
        print(f"GeneralDocumentClassifier: Classifying document {document.document_id}...")
        if not document.raw_text:
            print(f"GeneralDocumentClassifier: No raw text in document {document.document_id} to classify.")
            document.document_type = "unknown_no_text"
            return "unknown_no_text"

        text_upper = document.raw_text.upper()
        for doc_type, keywords in self.rules.items():
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    document.document_type = doc_type
                    print(f"GeneralDocumentClassifier: Document {document.document_id} classified as '{doc_type}'.")
                    return doc_type

        # Fallback classification if no rules match
        if "generic document" in document.raw_text.lower():
            document.document_type = "generic_report"
            print(f"GeneralDocumentClassifier: Document {document.document_id} classified as 'generic_report'.")
            return "generic_report"

        document.document_type = "unknown_general"
        print(f"GeneralDocumentClassifier: Document {document.document_id} classified as 'unknown_general'.")
        return "unknown_general"

# Example of a more sophisticated classifier (placeholder)
class MLDocumentClassifier(DocumentClassifier):
    """
    Placeholder for a machine learning-based document classifier.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        # In a real scenario, load the ML model here
        print(f"MLDocumentClassifier: Initialized. (Model loading from {model_path} would happen here).")

    def classify(self, document: Document) -> str:
        """
        Simulates classification using an ML model.
        """
        print(f"MLDocumentClassifier: Classifying document {document.document_id} using ML model...")
        if not document.raw_text:
            print(f"MLDocumentClassifier: No raw text in document {document.document_id}.")
            document.document_type = "unknown_ml_no_text"
            return "unknown_ml_no_text"

        # Simulate ML prediction
        # This would involve feature extraction from document.raw_text and model inference
        if "invoice" in document.raw_text.lower() and "total due" in document.raw_text.lower():
            predicted_type = "invoice_ml"
        elif "report" in document.raw_text.lower() and "summary" in document.raw_text.lower():
            predicted_type = "report_ml"
        else:
            predicted_type = "other_ml"

        document.document_type = predicted_type
        print(f"MLDocumentClassifier: Document {document.document_id} classified as '{predicted_type}'.")
        return predicted_type
