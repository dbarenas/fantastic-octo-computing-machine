from abc import ABC, abstractmethod
from typing import Any, Dict, List

class Document(ABC):
    """
    Abstract base class for a document.
    """
    def __init__(self, document_path: str, document_id: str):
        self.document_path = document_path
        self.document_id = document_id
        self.raw_text: str = ""
        self.document_type: str | None = None
        self.extracted_fields: Dict[str, Any] = {}
        self.validation_errors: List[str] = []

    @abstractmethod
    def load_content(self) -> None:
        """Loads the document content."""
        pass

class OCRExtractor(ABC):
    """
    Abstract base class for an OCR extractor.
    """
    @abstractmethod
    def extract_text(self, document: Document) -> str:
        """Extracts text from a document."""
        pass

class DocumentClassifier(ABC):
    """
    Abstract base class for a document classifier.
    """
    @abstractmethod
    def classify(self, document: Document) -> str:
        """Classifies the document type based on its content."""
        pass

class FieldRetriever(ABC):
    """
    Abstract base class for a field retriever.
    """
    @abstractmethod
    def retrieve_fields(self, document: Document) -> Dict[str, Any]:
        """Retrieves specific fields from a document based on its type."""
        pass

class Validator(ABC):
    """
    Abstract base class for a data validator.
    """
    @abstractmethod
    def validate(self, data: Any, rules: Dict[str, Any]) -> List[str]:
        """Validates data against a set of rules."""
        pass

class Process(ABC):
    """
    Abstract base class for a document processing workflow.
    """
    def __init__(self, process_id: str):
        self.process_id = process_id
        self.documents_to_process: List[Document] = []
        self.processed_documents: List[Document] = []
        self.process_errors: List[str] = []
        self.ocr_extractor: OCRExtractor | None = None
        self.document_classifier: DocumentClassifier | None = None
        self.field_retrievers: Dict[str, FieldRetriever] = {} # document_type -> retriever
        self.validators: Dict[str, List[Validator]] = {} # field_name -> list of validators

    @abstractmethod
    def add_document(self, document_path: str, document_id: str) -> None:
        """Adds a document to the processing queue."""
        pass

    @abstractmethod
    def set_ocr_extractor(self, extractor: OCRExtractor) -> None:
        """Sets the OCR extractor for the process."""
        pass

    @abstractmethod
    def set_document_classifier(self, classifier: DocumentClassifier) -> None:
        """Sets the document classifier for the process."""
        pass

    @abstractmethod
    def add_field_retriever(self, document_type: str, retriever: FieldRetriever) -> None:
        """Adds a field retriever for a specific document type."""
        pass

    @abstractmethod
    def add_validator(self, field_name: str, validator: Validator) -> None:
        """Adds a validator for a specific field."""
        pass

    def _get_document_instance(self, document_path: str, document_id: str) -> Document:
        """
        Factory method to create document instances.
        This should be overridden by subclasses if they use specific Document types.
        """
        # For now, let's assume a generic Document implementation will be available
        # This part might need adjustment based on how concrete Document types are handled.
        # raise NotImplementedError("Subclasses must implement _get_document_instance")
        # Temporarily, we'll create a placeholder. This will be refined in the next step.
        class GenericDocument(Document):
            def load_content(self) -> None:
                # In a real scenario, this would load content from self.document_path
                print(f"GenericDocument: Pretending to load content for {self.document_id} from {self.document_path}")
                # For demonstration, let's assume some dummy text is loaded
                self.raw_text = "This is dummy text from a generic document."
        return GenericDocument(document_path, document_id)


    def run(self) -> None:
        """
        Executes the document processing workflow.
        """
        if not self.ocr_extractor:
            self.process_errors.append("OCR extractor not set.")
            return
        if not self.document_classifier:
            self.process_errors.append("Document classifier not set.")
            return

        for doc_info in self.documents_to_process: # Assuming documents_to_process holds paths/ids for now
            # This needs to be adjusted based on how documents are added
            # For now, let's assume doc_info is a tuple (path, id)
            # This will be refined when add_document is fully implemented.
            # The current self.documents_to_process is List[Document],
            # but it's empty until add_document creates actual Document instances.
            # Let's adjust the loop to iterate over a temporary list of document paths/ids
            # and create Document instances inside the loop.

            # This part of the Process.run() method needs to be re-thought.
            # The documents should be actual Document objects added via add_document.
            # The current design of add_document in the ABC is just a signature.
            # Let's refine this in the concrete Process implementation.

            # For now, the logic will be:
            # 1. Iterate through self.documents_to_process (which should be populated by add_document)
            # 2. For each document:
            #    a. Load content (if not already loaded by add_document)
            #    b. Extract text using OCR
            #    c. Classify document
            #    d. Retrieve fields
            #    e. Validate fields
            #    f. Add to processed_documents or handle errors

            # This will be properly implemented in the concrete Process class.
            # The abstract run method here will be minimal or removed if all logic
            # moves to the concrete class. For now, let's keep it as a placeholder
            # for the general flow.
            pass

        print(f"Process {self.process_id} finished.")
        if self.process_errors:
            print("Errors occurred during processing:")
            for error in self.process_errors:
                print(f"- {error}")

    @abstractmethod
    def get_process_summary(self) -> Dict[str, Any]:
        """Returns a summary of the process execution."""
        pass

# Create __init__.py files to make them packages
# src/document_processing/__init__.py
# src/document_processing/core/__init__.py
