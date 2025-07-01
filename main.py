import os
import shutil

# Import core components (though not directly used, good for context)
from src.document_processing.core import (
    OCRExtractor,
    DocumentClassifier,
    FieldRetriever,
    Validator
)

# Import concrete implementations
from src.document_processing.impl import (
    PDFDocument,
    ImageDocument,
    TesseractOCRExtractor, # Keep for potential comparison or alternative setup
    TextractOCRExtractor,  # Import the new Textract extractor
    InvoiceClassifier,
    GeneralDocumentClassifier,
    InvoiceFieldRetriever,
    GeneralFieldRetriever,
    DataLengthValidator,
    RegexValidator,
    DateFormatValidator,
    FinancialProcess
)

def setup_dummy_files():
    """Creates some dummy files for the demonstration."""
    print("Setting up dummy files for demonstration...")
    os.makedirs("dummy_docs", exist_ok=True)

    # Dummy Invoice PDF (content will be simulated by OCR based on path)
    with open("dummy_docs/invoice_document_for_ocr.pdf", "w") as f:
        f.write("%PDF-1.4\n%Dummy PDF for invoice_document_for_ocr.pdf")

    # Dummy Generic Document PDF (content will be simulated by OCR based on path)
    with open("dummy_docs/generic_document_for_ocr.pdf", "w") as f:
        f.write("%PDF-1.4\n%Dummy PDF for generic_document_for_ocr.pdf")

    # Dummy Image Document (content will be simulated by OCR)
    with open("dummy_docs/photo_id_for_ocr.jpg", "w") as f:
        f.write("Dummy JPG content for photo_id_for_ocr.jpg") # Content not really parsed, path drives simulation

    # Dummy text file (will be handled by PDFDocument fallback or needs specific handler)
    with open("dummy_docs/notes.txt", "w") as f:
        f.write("This is a plain text file with some notes. It might be misclassified or handled by a fallback.")

    print("Dummy files created in 'dummy_docs/' directory.")

def cleanup_dummy_files():
    """Removes the dummy files and directory."""
    if os.path.exists("dummy_docs"):
        print("Cleaning up dummy files...")
        shutil.rmtree("dummy_docs")
        print("Dummy files cleaned up.")

def run_demo_process():
    """
    Demonstrates the setup and execution of a document processing workflow.
    """
    print("\n--- Starting Document Processing Demo ---")

    # 1. Setup: Create dummy files for processing
    setup_dummy_files()

    # 2. Instantiate components
    print("\n--- Initializing Components ---")
    # OCR Extractor
    # Option 1: Use Tesseract (offline, good for basic demo)
    # ocr_extractor = TesseractOCRExtractor()
    # print("Using TesseractOCRExtractor (simulated offline OCR)")

    # Option 2: Use AWS Textract (requires AWS credentials and network access)
    # IMPORTANT: Using TextractOCRExtractor will make actual calls to AWS Textract,
    # which may incur costs and requires AWS credentials to be configured.
    # Ensure your AWS environment is set up (e.g., via AWS CLI `aws configure`).
    try:
        # You might want to specify a region if not using the default
        # ocr_extractor = TextractOCRExtractor(region_name="your-aws-region")
        ocr_extractor = TextractOCRExtractor()
        print("Using TextractOCRExtractor (requires AWS credentials and may incur costs)")
    except Exception as e:
        print(f"Failed to initialize TextractOCRExtractor: {e}")
        print("Falling back to TesseractOCRExtractor for demo purposes.")
        ocr_extractor = TesseractOCRExtractor()
        print("Using TesseractOCRExtractor (simulated offline OCR)")


    # Classifiers
    # We can have a primary classifier and chain them or use a more sophisticated one.
    # For this demo, GeneralDocumentClassifier can be configured.
    # InvoiceClassifier can be specific to invoices.
    # Let's use GeneralDocumentClassifier with rules, and it can also call InvoiceClassifier if needed,
    # or the Process class can manage multiple classifiers.
    # For simplicity, the Process takes one main classifier.
    # We'll configure GeneralDocumentClassifier for multiple types.
    general_classifier_rules = {
        "invoice": ["INVOICE", "Invoice No"], # Keywords for invoice
        "id_card": ["ID CARD", "PASSPORT", "DRIVER LICENSE"], # Keywords for ID
        "generic_report": ["generic document", "report"]
    }
    document_classifier = GeneralDocumentClassifier(classification_rules=general_classifier_rules)
    # Alternative: If FinancialProcess was designed to use specific classifiers first,
    # it could try InvoiceClassifier then fallback to GeneralDocumentClassifier.
    # Our current Process takes one main classifier.

    # Field Retrievers
    # Retriever for Invoices
    invoice_retriever = InvoiceFieldRetriever()
    # Retriever for Generic Reports (example)
    generic_report_rules = {
        "serial_number": r"Serial Number: ([A-Z0-9-]+)",
        "report_date": r"Date: (\d{4}-\d{2}-\d{2})"
    }
    generic_report_retriever = GeneralFieldRetriever(retrieval_rules={"generic_report": generic_report_rules})
    # Retriever for ID cards (placeholder, simple example)
    id_card_rules = {
        "id_number": r"ID No[:\s]+([A-Z0-9]+)",
        "name": r"Name[:\s]+([A-Za-z\s]+)"
    }
    id_card_retriever = GeneralFieldRetriever(retrieval_rules={"id_card": id_card_rules})


    # Validators
    length_validator = DataLengthValidator()
    regex_validator = RegexValidator()
    date_validator = DateFormatValidator()

    # 3. Create and configure a Process
    print("\n--- Configuring Financial Process ---")
    financial_process = FinancialProcess(process_id="FINPROC-001")

    # Set components
    financial_process.set_ocr_extractor(ocr_extractor)
    financial_process.set_document_classifier(document_classifier)

    # Add field retrievers for different document types
    financial_process.add_field_retriever("invoice", invoice_retriever)
    financial_process.add_field_retriever("generic_report", generic_report_retriever)
    financial_process.add_field_retriever("id_card", id_card_retriever) # Assuming 'id_card' is a type our classifier can identify
    financial_process.add_field_retriever("default", GeneralFieldRetriever(retrieval_rules={})) # Fallback


    # Add validation rules for specific fields
    # For Invoices
    financial_process.add_validator_for_field("invoice_number", length_validator, {"min_length": 3, "max_length": 20})
    financial_process.add_validator_for_field("invoice_number", regex_validator, {"pattern": r"^[A-Z0-9-]+$"})
    financial_process.add_validator_for_field("invoice_date", date_validator, {"format": "YYYY-MM-DD"})
    # For Generic Reports
    financial_process.add_validator_for_field("serial_number", regex_validator, {"pattern": r"^[A-Z]{3}-\d+$"})
    financial_process.add_validator_for_field("report_date", date_validator, {"format": "YYYY-MM-DD"})
    # For ID Cards
    financial_process.add_validator_for_field("id_number", length_validator, {"min_length": 5})


    # 4. Add documents to the process
    print("\n--- Adding Documents to Process ---")
    financial_process.add_document(document_path="dummy_docs/invoice_document_for_ocr.pdf", document_id="DOC001")
    financial_process.add_document(document_path="dummy_docs/generic_document_for_ocr.pdf", document_id="DOC002")
    financial_process.add_document(document_path="dummy_docs/photo_id_for_ocr.jpg", document_id="DOC003") # This needs rules in classifier/retriever
    financial_process.add_document(document_path="dummy_docs/notes.txt", document_id="DOC004") # Will use fallback Document type

    # 5. Run the process
    print("\n--- Running Process ---")
    financial_process.run()

    # 6. Get and print the summary
    print("\n--- Process Summary ---")
    summary = financial_process.get_process_summary()

    print(f"Process ID: {summary['process_id']}")
    print(f"Overall Status: {summary['status']}")
    print(f"Total Documents Queued: {summary['total_documents_queued']}")
    print(f"Total Documents Processed: {summary['total_documents_processed']}")

    if summary['process_errors']:
        print("Process-Level Errors:")
        for err in summary['process_errors']:
            print(f"  - {err}")

    print("\nDocument Details:")
    for doc_summary in summary['documents']:
        print(f"  Document ID: {doc_summary['document_id']} (Path: {doc_summary['document_path']}, Class: {doc_summary['document_class']})")
        print(f"    Classified Type: {doc_summary['document_type_classified']}")
        print(f"    Extracted Fields: {doc_summary['extracted_fields']}")
        print(f"    Validation Errors: {doc_summary['validation_errors'] if doc_summary['validation_errors'] else 'None'}")
        # print(f"    Raw Text Snippet: {doc_summary['raw_text_snippet']}") # Can be verbose
        print("-" * 20)

    # 7. Cleanup
    cleanup_dummy_files()
    print("\n--- Document Processing Demo Finished ---")

if __name__ == "__main__":
    run_demo_process()
