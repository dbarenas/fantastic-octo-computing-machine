# Agent Instructions for Document Processing Framework

This document provides guidelines and instructions for AI agents working on this Document Processing Framework codebase.

## Core Principles

1.  **Maintain Abstraction**: The separation between `core` (interfaces) and `impl` (concrete implementations) is crucial. When adding new functionalities, always consider if it's a new type of an existing abstraction or a new abstraction altogether.
2.  **Extensibility First**: Design new components and modify existing ones with extensibility in mind. How would another developer (or another agent) easily add a variation of this component?
3.  **Modularity**: Components should be as self-contained as possible. Minimize tight coupling between concrete implementations. They should primarily rely on the interfaces from `core`.
4.  **Clarity and Readability**: Code should be well-documented with clear docstrings for classes and methods, especially public APIs and abstract methods. Type hinting is mandatory.
5.  **Simplicity (KISS)**: Prefer simple, understandable solutions over overly complex ones, especially for the example implementations. The framework should be easy to grasp.

## Development Guidelines

### 1. Adding New Components (Documents, Extractors, Classifiers, Retrievers, Validators, Processes)

*   **Interfaces First**: If a new *kind* of component is needed that doesn't fit existing abstractions, define its interface in `src/document_processing/core/base.py` first.
*   **Implementations in `impl`**: Place all concrete implementations in the appropriate file within `src/document_processing/impl/`.
*   **Update `__init__.py`**: Ensure any new concrete class intended for public use is exported in `src/document_processing/impl/__init__.py`. Similarly for new core interfaces in `src/document_processing/core/__init__.py`.
*   **Simulate External Dependencies**: For components that would normally interact with external services (e.g., OCR engines, cloud AI services, databases):
    *   Create a simulated version for easy testing and demonstration (as done with `TesseractOCRExtractor`). For live cloud services (e.g., `TextractOCRExtractor`), ensure they gracefully handle missing credentials or configurations, possibly by raising an informative error or having a no-op/fallback mode for local testing if appropriate.
    *   Clearly mark these as simulations or live integrations. Note what a real implementation would entail (e.g., API keys, SDK usage, IAM roles).
    *   Do not include actual API keys or sensitive credentials in the codebase. Components should rely on SDKs' standard credential discovery chains (environment variables, shared credential files, IAM roles).
    *   Document any required external dependencies (like `boto3`) in `requirements.txt`.
*   **Example Process (`FinancialProcess`)**: This process is an example. When adding fundamentally different process flows, consider creating a new class inheriting from `Process` rather than overcomplicating `FinancialProcess`.

### 2. Modifying Existing Components

*   **Backward Compatibility (Interfaces)**: Be very careful when modifying interfaces in `core/base.py`. Changes here can break all existing implementations. If a change is needed, consider if a new interface version or a new method is more appropriate.
*   **Focus on `Process.run()`**: The `run()` method in `Process` implementations (like `FinancialProcess`) is the orchestrator. When changing the flow (e.g., order of operations, conditional execution), this is the primary place to modify.
*   **Document Interaction**:
    *   `Document.load_content()`: Specific to the document type.
    *   `OCRExtractor.extract_text()`: Should update `document.raw_text`.
    *   `DocumentClassifier.classify()`: Should update `document.document_type`.
    *   `FieldRetriever.retrieve_fields()`: Should update `document.extracted_fields`.
    *   `Validator.validate()`: Operates on data, results are used by the `Process` to populate `document.validation_errors`.

### 3. Configuration and Rules

*   Many components (`GeneralDocumentClassifier`, `GeneralFieldRetriever`, `Validator` instances within a `Process`) are rule-driven.
*   Currently, these rules are often passed during instantiation (see `main.py`).
*   **Future Goal**: Move towards loading such configurations from external files (e.g., YAML, JSON). When working on features that involve complex rule sets, keep this future goal in mind. Design rule structures that would be easily serializable.

### 4. `main.py` Script

*   This script serves as a **demonstration and integration test**.
*   When adding new components, update `main.py` to showcase their usage if it makes sense for the demo scenario.
*   Ensure `main.py` runs without errors after your changes.
*   The `setup_dummy_files()` and `cleanup_dummy_files()` functions are important for the demo to be self-contained.

### 5. Testing (Future Enhancement)

*   While formal unit/integration tests are not yet part of this initial structure, any new logic should be written with testability in mind.
*   Think about how you would isolate and test each part of your new component.
*   When implementing complex logic (e.g., intricate regex in a retriever, complex validation rules), consider adding comments that explain the logic and edge cases, which will be helpful when tests are eventually written.

### 6. Logging (Future Enhancement)

*   Currently, `print()` statements are used for simplicity.
*   **Future Goal**: Integrate Python's `logging` module. When adding significant new processing steps or error handling, consider where log messages (DEBUG, INFO, WARNING, ERROR) would be appropriate.

## Before Submitting Changes

1.  **Run `main.py`**: Ensure the demo script completes successfully.
2.  **Review against Core Principles**: Does your change align with abstraction, extensibility, and modularity?
3.  **Check `README.md`**: If you've added a new type of component or a significant feature that users should know how to extend, update `README.md` accordingly.
4.  **Clarity**: Is the code clear, well-commented (where necessary), and type-hinted?

By following these guidelines, we can ensure the framework remains robust, maintainable, and easy to extend.
