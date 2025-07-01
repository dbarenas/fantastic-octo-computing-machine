from src.document_processing.core.base import Process, Document, OCRExtractor, DocumentClassifier, FieldRetriever, Validator
from src.document_processing.impl.documents import PDFDocument, ImageDocument # Example document types
from typing import Any, Dict, List, Type

class FinancialProcess(Process):
    """
    Example implementation for a financial document processing workflow.
    This process can handle different types of documents (PDFs, Images).
    """

    # Define which Document class to use for which file extension
    DOCUMENT_TYPE_MAPPING: Dict[str, Type[Document]] = {
        ".pdf": PDFDocument,
        ".png": ImageDocument,
        ".jpg": ImageDocument,
        ".jpeg": ImageDocument,
        # Add more mappings as needed
    }

    def __init__(self, process_id: str):
        super().__init__(process_id)
        self.overall_status: str = "Initialized"
        # Field-specific validation rules, field_name -> {validator_instance: rules_dict}
        self.field_validation_rules: Dict[str, Dict[Validator, Dict[str, Any]]] = {}

    def _get_document_instance(self, document_path: str, document_id: str) -> Document:
        """
        Creates a document instance based on file extension.
        """
        import os
        _, ext = os.path.splitext(document_path)
        doc_class = self.DOCUMENT_TYPE_MAPPING.get(ext.lower())

        if doc_class:
            return doc_class(document_path, document_id)
        else:
            # Fallback or raise error
            print(f"Warning: No specific Document class for extension '{ext}'. Using generic PDFDocument as fallback for {document_id}.")
            # As a fallback, we could use a default or raise an error.
            # For this example, let's default to PDFDocument if unknown,
            # or better, have a GenericDocument if one was defined.
            # Using PDFDocument might not be ideal if it's not a PDF.
            # This highlights the need for careful _get_document_instance design.
            # Let's assume PDFDocument can handle it or throw an error during load_content.
            return PDFDocument(document_path, document_id) # Or raise ValueError

    def add_document(self, document_path: str, document_id: str) -> None:
        """Adds a document to the processing queue by creating an appropriate Document instance."""
        try:
            doc_instance = self._get_document_instance(document_path, document_id)
            self.documents_to_process.append(doc_instance)
            print(f"FinancialProcess [{self.process_id}]: Document {document_id} ({doc_instance.__class__.__name__}) added from path {document_path}.")
        except ValueError as e:
            self.process_errors.append(f"Failed to add document {document_id}: {e}")
            print(f"Error adding document {document_id}: {e}")
        except Exception as e_gen:
            self.process_errors.append(f"Unexpected error adding document {document_id}: {e_gen}")
            print(f"Unexpected error adding document {document_id}: {e_gen}")


    def set_ocr_extractor(self, extractor: OCRExtractor) -> None:
        self.ocr_extractor = extractor
        print(f"FinancialProcess [{self.process_id}]: OCR Extractor '{extractor.__class__.__name__}' set.")

    def set_document_classifier(self, classifier: DocumentClassifier) -> None:
        self.document_classifier = classifier
        print(f"FinancialProcess [{self.process_id}]: Document Classifier '{classifier.__class__.__name__}' set.")

    def add_field_retriever(self, document_type: str, retriever: FieldRetriever) -> None:
        self.field_retrievers[document_type] = retriever
        print(f"FinancialProcess [{self.process_id}]: Field Retriever '{retriever.__class__.__name__}' added for document type '{document_type}'.")

    def add_validator_for_field(self, field_name: str, validator: Validator, rules: Dict[str, Any]) -> None:
        """Adds a validator with specific rules for a given field name."""
        if field_name not in self.field_validation_rules:
            self.field_validation_rules[field_name] = {}
        self.field_validation_rules[field_name][validator] = rules
        # The base class `validators` dict is not used in this refined approach.
        # We store validators and their rules together per field.
        print(f"FinancialProcess [{self.process_id}]: Validator '{validator.__class__.__name__}' with rules {rules} added for field '{field_name}'.")

    # This method from ABC is not directly used if add_validator_for_field is preferred.
    # We can choose to not implement it or adapt it.
    def add_validator(self, field_name: str, validator: Validator) -> None:
        # This method is less useful without rules. We'll use add_validator_for_field instead.
        # Or, it could add a validator with default/no rules, which is less practical.
        print(f"Warning: FinancialProcess.add_validator called for {field_name} with {validator.__class__.__name__}. Consider using add_validator_for_field with rules.")
        if field_name not in self.field_validation_rules:
            self.field_validation_rules[field_name] = {}
        # Adding validator without specific rules, assuming validator might have default behavior or rules are set elsewhere.
        self.field_validation_rules[field_name][validator] = {}


    def run(self) -> None:
        print(f"\nStarting FinancialProcess [{self.process_id}]...")
        self.overall_status = "Running"

        if not self.ocr_extractor:
            self.process_errors.append("OCR extractor not set.")
            self.overall_status = "Failed"
            print("Error: OCR extractor not set. Aborting process.")
            return
        if not self.document_classifier:
            self.process_errors.append("Document classifier not set.")
            self.overall_status = "Failed"
            print("Error: Document classifier not set. Aborting process.")
            return

        if not self.documents_to_process:
            print("No documents to process.")
            self.overall_status = "Completed (No Data)"
            return

        for doc in self.documents_to_process:
            try:
                print(f"\nProcessing document: {doc.document_id} ({doc.document_path})")

                # 1. Load content (specific to document type)
                doc.load_content()
                if hasattr(doc, 'raw_text') and not doc.raw_text and not isinstance(doc, ImageDocument): # ImageDocument content is path for OCR
                    print(f"Warning: No content loaded for document {doc.document_id}.")
                    # Decide if to continue or mark as error

                # 2. Extract text using OCR
                print(f"Step: OCR Extraction for {doc.document_id}")
                raw_text = self.ocr_extractor.extract_text(doc) # OCR updates doc.raw_text
                if not raw_text:
                    doc.validation_errors.append("OCR failed to extract text.")
                    print(f"Error: OCR failed for {doc.document_id}. Skipping further processing for this document.")
                    self.processed_documents.append(doc)
                    continue
                # print(f"Extracted text for {doc.document_id}: {raw_text[:100]}...") # Keep it short

                # 3. Classify document
                print(f"Step: Document Classification for {doc.document_id}")
                doc_type = self.document_classifier.classify(doc) # Classifier updates doc.document_type
                if not doc_type or doc_type in ["unknown", "unknown_no_text", "unknown_general", "unknown_ml_no_text"]:
                    doc.validation_errors.append(f"Document classification failed or type is unknown ('{doc_type}').")
                    print(f"Warning: Classification for {doc.document_id} resulted in '{doc_type}'. May impact field retrieval.")
                    # Optionally, skip if type is critical and unknown
                    # For now, we'll try to proceed if a general retriever exists.

                # 4. Retrieve fields
                print(f"Step: Field Retrieval for {doc.document_id} (type: {doc.document_type})")
                retriever = self.field_retrievers.get(doc.document_type)
                if not retriever:
                    # Try a fallback "general" or "default" retriever if configured
                    retriever = self.field_retrievers.get("default") # Or some other agreed-upon key for general retriever
                    if not retriever:
                        doc.validation_errors.append(f"No field retriever found for document type '{doc.document_type}'.")
                        print(f"Error: No field retriever for {doc.document_id} (type: {doc.document_type}). Skipping field retrieval.")
                        self.processed_documents.append(doc)
                        continue
                    else:
                        print(f"Using default field retriever for {doc.document_id}.")

                extracted_fields = retriever.retrieve_fields(doc) # Retriever updates doc.extracted_fields
                print(f"Retrieved fields for {doc.document_id}: {extracted_fields}")

                # 5. Validate fields
                print(f"Step: Field Validation for {doc.document_id}")
                if not extracted_fields:
                    print(f"No fields extracted for {doc.document_id}. Skipping validation.")
                else:
                    for field_name, field_value in extracted_fields.items():
                        if field_name in self.field_validation_rules:
                            for validator, rules in self.field_validation_rules[field_name].items():
                                print(f"Validating field '{field_name}' (value: '{field_value}') with {validator.__class__.__name__} and rules {rules}")
                                errors = validator.validate(field_value, rules)
                                if errors:
                                    doc.validation_errors.extend([f"Field '{field_name}': {err}" for err in errors])
                                    print(f"Validation errors for '{field_name}': {errors}")
                        else:
                            print(f"No validation rules defined for field '{field_name}'.")

                if doc.validation_errors:
                    print(f"Document {doc.document_id} has validation errors: {doc.validation_errors}")

                self.processed_documents.append(doc)
                print(f"Finished processing document: {doc.document_id}")

            except Exception as e:
                error_msg = f"Error processing document {doc.document_id}: {e}"
                print(error_msg)
                self.process_errors.append(error_msg)
                if doc: # If doc instance exists, add error to it as well
                    doc.validation_errors.append(f"Critical processing error: {e}")
                    self.processed_documents.append(doc) # Add even if failed, to have a record
                # Optionally re-raise or handle more gracefully

        self.overall_status = "Completed"
        if self.process_errors:
            self.overall_status = "Completed with Errors"

        print(f"\nFinancialProcess [{self.process_id}] finished with status: {self.overall_status}.")
        if self.process_errors:
            print("Process-level errors occurred:")
            for error in self.process_errors:
                print(f"- {error}")

    def get_process_summary(self) -> Dict[str, Any]:
        summary = {
            "process_id": self.process_id,
            "status": self.overall_status,
            "total_documents_queued": len(self.documents_to_process),
            "total_documents_processed": len(self.processed_documents),
            "process_errors": self.process_errors,
            "documents": []
        }
        for doc in self.processed_documents:
            doc_summary = {
                "document_id": doc.document_id,
                "document_path": doc.document_path,
                "document_class": doc.__class__.__name__,
                "document_type_classified": doc.document_type,
                "extracted_fields": doc.extracted_fields,
                "validation_errors": doc.validation_errors,
                "raw_text_snippet": doc.raw_text[:100] + "..." if doc.raw_text else "N/A"
            }
            summary["documents"].append(doc_summary)
        return summary
