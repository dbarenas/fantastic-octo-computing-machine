from src.document_processing.core.base import FieldRetriever, Document
from typing import Any, Dict
import re

class InvoiceFieldRetriever(FieldRetriever):
    """
    Example implementation for retrieving fields from an invoice.
    """
    def retrieve_fields(self, document: Document) -> Dict[str, Any]:
        """
        Retrieves fields like invoice number, date, and total from invoice text.
        Assumes document.document_type has been set to "invoice".
        """
        print(f"InvoiceFieldRetriever: Retrieving fields for document {document.document_id} (type: {document.document_type})...")
        if document.document_type != "invoice" and document.document_type != "invoice_ml": # Also handle ML classified invoices
            print(f"InvoiceFieldRetriever: Document {document.document_id} is not an invoice. Skipping field retrieval.")
            return {}

        if not document.raw_text:
            print(f"InvoiceFieldRetriever: No raw text in document {document.document_id} to retrieve fields from.")
            return {}

        extracted_fields: Dict[str, Any] = {}

        # Example: Retrieve Invoice Number
        match_invoice_no = re.search(r"Invoice No[:\s]+([A-Z0-9-]+)", document.raw_text, re.IGNORECASE)
        if match_invoice_no:
            extracted_fields["invoice_number"] = match_invoice_no.group(1)

        # Example: Retrieve Date
        match_date = re.search(r"Date[:\s]+(\d{4}-\d{2}-\d{2})", document.raw_text, re.IGNORECASE)
        if match_date:
            extracted_fields["invoice_date"] = match_date.group(1)

        # Example: Retrieve Total
        match_total = re.search(r"Total[:\s]+\$?([\d,]+\.?\d*)", document.raw_text, re.IGNORECASE)
        if match_total:
            extracted_fields["total_amount"] = float(match_total.group(1).replace(",", ""))

        document.extracted_fields.update(extracted_fields)
        print(f"InvoiceFieldRetriever: Fields retrieved for {document.document_id}: {extracted_fields}")
        return extracted_fields

class GeneralFieldRetriever(FieldRetriever):
    """
    A general field retriever using regex patterns defined per document type.
    """
    def __init__(self, retrieval_rules: Dict[str, Dict[str, str]]):
        # retrieval_rules format: {"doc_type_name": {"field_name": "regex_pattern", ...}, ...}
        # Example: {"generic_report": {"serial_number": "Serial Number: ([A-Z0-9-]+)", "report_date": "Date: (\d{4}-\d{2}-\d{2})"}}
        self.retrieval_rules = retrieval_rules
        print(f"GeneralFieldRetriever initialized with rules for doc types: {list(self.retrieval_rules.keys())}")

    def retrieve_fields(self, document: Document) -> Dict[str, Any]:
        print(f"GeneralFieldRetriever: Retrieving fields for document {document.document_id} (type: {document.document_type})...")

        if not document.document_type or document.document_type not in self.retrieval_rules:
            print(f"GeneralFieldRetriever: No retrieval rules for document type '{document.document_type}' or type not set. Skipping.")
            return {}

        if not document.raw_text:
            print(f"GeneralFieldRetriever: No raw text in document {document.document_id}.")
            return {}

        rules_for_type = self.retrieval_rules[document.document_type]
        extracted_fields: Dict[str, Any] = {}

        for field_name, pattern in rules_for_type.items():
            match = re.search(pattern, document.raw_text)
            if match:
                # If regex has groups, try to get the first group, else the full match.
                extracted_fields[field_name] = match.group(1) if match.groups() else match.group(0)

        document.extracted_fields.update(extracted_fields)
        print(f"GeneralFieldRetriever: Fields retrieved for {document.document_id}: {extracted_fields}")
        return extracted_fields

# Placeholder for a more advanced retriever (e.g., using Named Entity Recognition)
class NERFieldRetriever(FieldRetriever):
    """
    Placeholder for a field retriever using NER models.
    """
    def __init__(self, model_path: str):
        self.model_path = model_path
        # Load NER model here
        print(f"NERFieldRetriever: Initialized. (NER model from {model_path} would be loaded here).")

    def retrieve_fields(self, document: Document) -> Dict[str, Any]:
        print(f"NERFieldRetriever: Retrieving fields for document {document.document_id} using NER...")
        if not document.raw_text:
            print(f"NERFieldRetriever: No raw text in document {document.document_id}.")
            return {}

        # Simulate NER processing
        extracted_fields: Dict[str, Any] = {}
        # Example: if text contains "Payment due by 2023-12-31"
        if "payment due by" in document.raw_text.lower():
            date_match = re.search(r"payment due by (\d{4}-\d{2}-\d{2})", document.raw_text, re.IGNORECASE)
            if date_match:
                extracted_fields["due_date_ner"] = date_match.group(1)

        if "Acme Corp" in document.raw_text:
             extracted_fields["organization_ner"] = "Acme Corp"

        document.extracted_fields.update(extracted_fields)
        print(f"NERFieldRetriever: Fields retrieved for {document.document_id}: {extracted_fields}")
        return extracted_fields
