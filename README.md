# Document Processing Framework

This project provides a flexible and extensible framework for processing various types of documents. It follows a pipeline approach: document loading, OCR text extraction, document type classification, field retrieval, and data validation. The framework is designed with abstraction in mind, allowing developers to easily add new document types, processing components, and define complex workflows.

## Project Structure

```
.
├── src/
│   └── document_processing/
│       ├── __init__.py
│       ├── core/               # Abstract base classes and interfaces
│       │   ├── __init__.py
│       │   └── base.py
│       ├── impl/               # Concrete implementations
│       │   ├── __init__.py
│       │   ├── classifiers.py
│       │   ├── documents.py
│       │   ├── extractors.py
│       │   ├── processes.py
│       │   ├── retrievers.py
│       │   └── validators.py
│       └── utils/              # Utility functions (currently empty)
│           └── __init__.py
├── main.py                     # Example script demonstrating framework usage
└── README.md                   # This file
```

-   **`src/document_processing/core/base.py`**: Defines the abstract base classes (interfaces) for all major components:
    -   `Document`: Represents a generic document.
    -   `OCRExtractor`: Interface for OCR engines.
    -   `DocumentClassifier`: Interface for classifying document types.
    -   `FieldRetriever`: Interface for retrieving specific fields from a document.
    -   `Validator`: Interface for validating extracted data.
    -   `Process`: Abstract base class for a document processing workflow.
-   **`src/document_processing/impl/`**: Contains concrete implementations of the interfaces defined in `core`.
    -   `documents.py`: Examples like `PDFDocument`, `ImageDocument`.
    -   `extractors.py`: Examples like `TesseractOCRExtractor`.
    -   `classifiers.py`: Examples like `InvoiceClassifier`, `GeneralDocumentClassifier`.
    -   `retrievers.py`: Examples like `InvoiceFieldRetriever`, `GeneralFieldRetriever`.
    -   `validators.py`: Examples like `DataLengthValidator`, `RegexValidator`.
    -   `processes.py`: Example `FinancialProcess` orchestrating the steps.
-   **`src/document_processing/utils/`**: Intended for helper functions or shared utilities.
-   **`main.py`**: A script that demonstrates how to:
    -   Instantiate and configure processing components.
    -   Set up a `Process` (e.g., `FinancialProcess`).
    -   Add documents to the process.
    -   Run the process.
    -   Retrieve a summary of the processing results.

## Core Concepts

1.  **Document**: An abstraction of a file to be processed. Each document instance handles its own content loading.
2.  **OCRExtractor**: Responsible for extracting raw text from a document.
3.  **DocumentClassifier**: Determines the type of a document (e.g., "invoice", "report", "id_card") based on its content.
4.  **FieldRetriever**: Extracts specific data fields (e.g., invoice number, total amount) from a document, typically based on its classified type.
5.  **Validator**: Checks if the extracted data fields meet certain criteria (e.g., length, format, allowed values).
6.  **Process**: Orchestrates the entire workflow. It takes a list of documents and applies the configured extractors, classifiers, retrievers, and validators to each.

## How to Extend the Framework

The framework is designed for extensibility. Here’s how you can add custom components:

### 1. Adding a New Document Type

-   Create a new class that inherits from `Document` (in `src.document_processing.core.base`).
-   Implement the `load_content(self)` method to handle the specifics of loading this document type (e.g., parsing a specific XML format, connecting to a database).
-   **Example**:
    ```python
    # In src/document_processing/impl/documents.py (or a new file)
    from src.document_processing.core import Document
    from typing import Any # Added for example

    class MyCustomDocument(Document):
        def __init__(self, document_path: str, document_id: str, custom_param: Any):
            super().__init__(document_path, document_id)
            self.custom_param = custom_param
            # Add other specific attributes

        def load_content(self) -> None:
            print(f"MyCustomDocument [{self.document_id}]: Loading content using custom logic...")
            # Your logic to load content into self.raw_text or other attributes
            self.raw_text = f"Content from {self.document_path} with {self.custom_param}"
    ```
-   Update the `DOCUMENT_TYPE_MAPPING` in your concrete `Process` implementation (e.g., `FinancialProcess`) if you want it to automatically instantiate your new document type based on file extension.

### 2. Adding a New OCR Extractor

-   Create a new class that inherits from `OCRExtractor`.
-   Implement the `extract_text(self, document: Document) -> str` method to interface with your chosen OCR engine or service.
-   **Example**:
    ```python
    # In src/document_processing/impl/extractors.py
    from src.document_processing.core import OCRExtractor, Document

    class MyOCREngine(OCRExtractor):
        def extract_text(self, document: Document) -> str:
            # Logic to call your OCR engine with document.document_path or content
            text = f"Text extracted by MyOCREngine from {document.document_id}"
            document.raw_text = text # Important: Update the document's raw_text
            return text
    ```

### 3. Adding a New Document Classifier

-   Create a new class that inherits from `DocumentClassifier`.
-   Implement the `classify(self, document: Document) -> str` method. This method should analyze `document.raw_text` and return a string representing the document type.
-   **Example**:
    ```python
    # In src/document_processing/impl/classifiers.py
    from src.document_processing.core import DocumentClassifier, Document

    class MyCustomClassifier(DocumentClassifier):
        def classify(self, document: Document) -> str:
            if "confidential report" in document.raw_text.lower():
                document.document_type = "confidential_report"
                return "confidential_report"
            document.document_type = "unknown"
            return "unknown"
    ```

### 4. Adding a New Field Retriever

-   Create a new class that inherits from `FieldRetriever`.
-   Implement the `retrieve_fields(self, document: Document) -> Dict[str, Any]` method. This method should parse `document.raw_text` (and potentially use `document.document_type`) to extract relevant data.
-   **Example**:
    ```python
    # In src/document_processing/impl/retrievers.py
    from src.document_processing.core import FieldRetriever, Document
    from typing import Dict, Any

    class ConfidentialReportRetriever(FieldRetriever):
        def retrieve_fields(self, document: Document) -> Dict[str, Any]:
            fields = {}
            if document.document_type == "confidential_report":
                # Your logic to find fields, e.g., using regex
                fields["title"] = "Some Title" # Placeholder
            document.extracted_fields.update(fields) # Ensure fields are stored in the document
            return fields
    ```

### 5. Adding a New Validator

-   Create a new class that inherits from `Validator`.
-   Implement the `validate(self, data: Any, rules: Dict[str, Any]) -> List[str]` method. This method checks the given `data` against the provided `rules` and returns a list of error messages (empty if valid).
-   **Example**:
    ```python
    # In src/document_processing/impl/validators.py
    from src.document_processing.core import Validator
    from typing import Any, Dict, List

    class MyCustomValidator(Validator):
        def validate(self, data: Any, rules: Dict[str, Any]) -> List[str]:
            errors = []
            expected_value = rules.get("expected_value")
            if data != expected_value:
                errors.append(f"Value '{data}' does not match expected '{expected_value}'.")
            return errors
    ```

### 6. Adding a New Process Type

-   Create a new class that inherits from `Process`.
-   Implement the abstract methods:
    -   `add_document(...)` (or rely on a refined `_get_document_instance` as in `FinancialProcess`)
    -   `set_ocr_extractor(...)`
    -   `set_document_classifier(...)`
    -   `add_field_retriever(...)`
    -   `add_validator(...)` (or a more specific version like `add_validator_for_field` in `FinancialProcess`)
    -   `run()`: This is the core orchestration logic. You can customize the sequence of operations, error handling, and logging.
    -   `get_process_summary()`
-   You might also want to override `_get_document_instance` to control how `Document` objects are created (as shown in `FinancialProcess` with `DOCUMENT_TYPE_MAPPING`).

## Running the Demo

The `main.py` script provides a demonstration of how to use the framework:

1.  It sets up some dummy files in a `dummy_docs/` directory.
2.  It instantiates various components (OCR extractor, classifier, retrievers, validators).
3.  It creates a `FinancialProcess` and configures it with these components and validation rules.
4.  It adds the dummy documents to the process.
5.  It runs the process.
6.  It prints a detailed summary of the processing, including extracted fields and validation errors for each document.
7.  It cleans up the dummy files.

To run the demo:
```bash
python main.py
```

This will showcase the flow of operations and how different components interact. You can modify `main.py` to experiment with different configurations or new components you create.

## Future Considerations / Potential Improvements
- **Configuration Management**: Load process configurations (component choices, rules, mappings) from external files (e.g., YAML, JSON) instead of hardcoding in `main.py`.
- **Plugin System**: A more dynamic way to discover and register new components.
- **Asynchronous Processing**: For I/O bound tasks like OCR or external API calls, using `asyncio` could improve performance for batch processing.
- **Error Handling and Resilience**: More sophisticated error handling, retries, and dead-letter queues for failed documents.
- **Logging**: Integrate a structured logging library (e.g., `logging` module) throughout the framework.
- **Testing**: Comprehensive unit and integration tests for all components.
- **Dependency Injection**: A more formal DI container could manage component dependencies.
- **Chaining Components**: Allow chaining of classifiers or retrievers (e.g., a primary classifier, then a more specific one if the first classifies as "invoice").
- **Cross-Document Validation**: The current `Process` is document-centric. For validation rules that span multiple documents within a process, the `Process` class would need to be enhanced to collect all data first, then apply cross-document rules.
```
