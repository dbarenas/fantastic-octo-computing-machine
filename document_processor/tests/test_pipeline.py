import pytest
# from pipeline import DocumentProcessingPipeline # Actual pipeline
# from models import ProcessedDocument, DocumentMetadata, ExtractedData, ValidationResult # Actual models
# import os
# import uuid
# from datetime import datetime

# --- Mocks and Placeholders for Pipeline Dependencies ---
# These would be replaced by actual or more sophisticated mocks in full testing.

# Mock Pydantic Models (if not importing actual ones for some reason in this test file)
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class MockDocumentMetadata:
    def __init__(self, document_id, file_name, file_type, upload_date, processing_status, error_message=None):
        self.document_id = document_id
        self.file_name = file_name
        self.file_type = file_type
        self.upload_date = upload_date
        self.processing_status = processing_status
        self.error_message = error_message

class MockExtractedData:
    def __init__(self, document_type, fields):
        self.document_type = document_type
        self.fields = fields

class MockValidationResult:
    def __init__(self, is_valid, details):
        self.is_valid = is_valid
        self.details = details

class MockProcessedDocument:
    def __init__(self, metadata, extracted_data=None, validation_result=None, raw_text=None):
        self.metadata = metadata
        self.extracted_data = extracted_data
        self.validation_result = validation_result
        self.raw_text = raw_text

# Mock TextractClient
class MockTextractClient:
    def extract_text(self, document_path_or_bytes): # Simplified method name
        if "fail_ocr" in document_path_or_bytes:
            return None
        return f"Mock OCR text from {document_path_or_bytes}. Content: Certificado Final de Obra. Director: Juan."

# Mock DocumentClassifier
class MockDocumentClassifier:
    def __init__(self, text):
        self.text = text.lower()
    def classify(self):
        if "fail_classification" in self.text:
            return None
        if "certificado final" in self.text:
            return "certificado_final"
        if "factura" in self.text:
            return "factura"
        return "unknown_type"

# Mock Processor (Extractor & Validator) Factory and Instance
class MockDocumentProcessor:
    def __init__(self, text, doc_type):
        self.text = text
        self.doc_type = doc_type
    def extract(self):
        if "fail_extraction" in self.text:
            raise ValueError("Simulated extraction error")
        if self.doc_type == "certificado_final":
            return {"fecha": "10/10/2023", "firmas": True}
        return {"generic_field": "value"}
    def validate(self, data):
        if "fail_validation" in self.text: # Using text as a hack to trigger failure
            raise ValueError("Simulated validation error")
        if self.doc_type == "certificado_final" and data.get("fecha") == "10/10/2023":
            return {"is_valid": True, "details": {"fecha_check": "ok"}}
        return {"is_valid": False, "details": {"reason": "mock failure"}}

def mock_get_processor(doc_type, text):
    if doc_type == "unknown_type" or "fail_processor" in text:
        return None
    return MockDocumentProcessor(text, doc_type)

# Mock DB store function
mock_stored_data = []
def mock_store_document_data(processed_doc: MockProcessedDocument):
    mock_stored_data.append(processed_doc)
    # print(f"Mock storing document: {processed_doc.metadata.document_id}, Status: {processed_doc.metadata.processing_status}")
    return True

# --- The Pipeline (Simplified version for testing, mirroring pipeline.py structure) ---
# In a real test, you'd import the actual DocumentProcessingPipeline
class DocumentProcessingPipelineForTest:
    def __init__(self, document_path: str, file_name: str, file_type: str):
        self.document_path = document_path
        self.file_name = file_name
        self.file_type = file_type
        self.document_id = str(uuid.uuid4())

        self.textract_client = MockTextractClient()
        # self.db_inserter = mock_store_document_data # Direct function call

        self.metadata = MockDocumentMetadata(
            document_id=self.document_id, file_name=self.file_name, file_type=self.file_type,
            upload_date=datetime.now(), processing_status="pending"
        )
        self.raw_text = None
        self.extracted_data_model = None
        self.validation_result_model = None

    def run(self) -> MockProcessedDocument:
        self.metadata.processing_status = "processing_ocr"
        self.raw_text = self.textract_client.extract_text(self.document_path)
        if not self.raw_text:
            self.metadata.processing_status = "error_ocr"
            self.metadata.error_message = "OCR failed."
            mock_store_document_data(self._build_processed_document())
            return self._build_processed_document()

        self.metadata.processing_status = "processing_classification"
        classifier = MockDocumentClassifier(self.raw_text)
        doc_type = classifier.classify()
        if not doc_type:
            self.metadata.processing_status = "error_classification"
            self.metadata.error_message = "Classification failed."
            mock_store_document_data(self._build_processed_document())
            return self._build_processed_document()

        self.metadata.processing_status = "processing_extraction"
        processor = mock_get_processor(doc_type, self.raw_text)
        if not processor:
            self.metadata.processing_status = "error_no_processor"
            self.metadata.error_message = f"No processor for {doc_type}."
            mock_store_document_data(self._build_processed_document())
            return self._build_processed_document()

        try:
            extracted_fields = processor.extract()
            self.extracted_data_model = MockExtractedData(document_type=doc_type, fields=extracted_fields)
        except Exception as e:
            self.metadata.processing_status = "error_extraction"
            self.metadata.error_message = f"Extraction failed: {e}"
            mock_store_document_data(self._build_processed_document())
            return self._build_processed_document()

        self.metadata.processing_status = "processing_validation"
        try:
            validation_output = processor.validate(self.extracted_data_model.fields)
            self.validation_result_model = MockValidationResult(**validation_output)
            self.metadata.processing_status = "completed" if self.validation_result_model.is_valid else "completed_with_validation_issues"
        except Exception as e:
            self.metadata.processing_status = "error_validation"
            self.metadata.error_message = f"Validation failed: {e}"
            mock_store_document_data(self._build_processed_document())
            return self._build_processed_document()

        mock_store_document_data(self._build_processed_document())
        return self._build_processed_document()

    def _build_processed_document(self) -> MockProcessedDocument:
        return MockProcessedDocument(
            metadata=self.metadata, raw_text=self.raw_text,
            extracted_data=self.extracted_data_model, validation_result=self.validation_result_model
        )
# --- End Simplified Pipeline ---


@pytest.fixture(autouse=True)
def clear_mock_db():
    mock_stored_data.clear()

def test_pipeline_successful_run():
    """Test a successful run through the pipeline."""
    # Create a dummy file or path for the test
    dummy_file_path = "test_docs/certificado_sample.pdf" # Actual file not needed for mock

    pipeline = DocumentProcessingPipelineForTest(dummy_file_path, "certificado_sample.pdf", ".pdf")
    result = pipeline.run()

    assert result.metadata.processing_status == "completed"
    assert result.raw_text is not None
    assert "certificado final" in result.raw_text.lower() # From mock OCR
    assert result.extracted_data is not None
    assert result.extracted_data.document_type == "certificado_final"
    assert result.extracted_data.fields.get("fecha") == "10/10/2023"
    assert result.validation_result is not None
    assert result.validation_result.is_valid is True
    assert len(mock_stored_data) == 1
    assert mock_stored_data[0].metadata.document_id == result.metadata.document_id

def test_pipeline_ocr_failure():
    pipeline = DocumentProcessingPipelineForTest("test_docs/fail_ocr.pdf", "fail_ocr.pdf", ".pdf")
    result = pipeline.run()
    assert result.metadata.processing_status == "error_ocr"
    assert result.metadata.error_message == "OCR failed."
    assert result.raw_text is None
    assert len(mock_stored_data) == 1

def test_pipeline_classification_failure():
    # Textract mock will return text, but classifier mock will fail
    pipeline = DocumentProcessingPipelineForTest("test_docs/fail_classification_doc.txt", "fail_class.txt", ".txt")
    # Modify raw_text in pipeline's textract_client mock or pass specific content
    pipeline.textract_client.extract_text = lambda x: "Text that will fail_classification"

    result = pipeline.run()
    assert result.metadata.processing_status == "error_classification"
    assert result.raw_text == "Text that will fail_classification" # OCR succeeded
    assert result.extracted_data is None
    assert len(mock_stored_data) == 1

def test_pipeline_no_processor_failure():
    pipeline = DocumentProcessingPipelineForTest("test_docs/no_processor_doc.txt", "no_proc.txt", ".txt")
    # Ensure OCR and classification return something that leads to no processor
    pipeline.textract_client.extract_text = lambda x: "Text for unknown_type" # Classifier returns unknown_type
    # MockDocumentClassifier for "Text for unknown_type" will return "unknown_type"
    # mock_get_processor for "unknown_type" will return None

    result = pipeline.run()
    assert result.metadata.processing_status == "error_no_processor"
    assert result.metadata.error_message == "No processor for unknown_type."
    assert len(mock_stored_data) == 1

def test_pipeline_extraction_failure():
    pipeline = DocumentProcessingPipelineForTest("test_docs/fail_extraction_doc.pdf", "fail_extract.pdf", ".pdf")
    # Ensure OCR and classification succeed, but extraction step fails
    # The text "fail_extraction" will trigger this in MockDocumentProcessor
    pipeline.textract_client.extract_text = lambda x: "Certificado Final de Obra. fail_extraction"

    result = pipeline.run()
    assert result.metadata.processing_status == "error_extraction"
    assert "Extraction failed: Simulated extraction error" in result.metadata.error_message
    assert result.extracted_data is None # Should be None or not fully populated
    assert len(mock_stored_data) == 1

def test_pipeline_validation_failure_step(): # Renamed to avoid conflict
    pipeline = DocumentProcessingPipelineForTest("test_docs/fail_validation_doc.pdf", "fail_validate.pdf", ".pdf")
    # Ensure OCR, classification, extraction succeed, but validation step fails
    pipeline.textract_client.extract_text = lambda x: "Certificado Final de Obra. fail_validation" # This text triggers validation error

    result = pipeline.run()
    assert result.metadata.processing_status == "error_validation"
    assert "Validation failed: Simulated validation error" in result.metadata.error_message
    assert result.extracted_data is not None # Extraction was fine
    assert result.validation_result is None # Validation object not created or error state
    assert len(mock_stored_data) == 1

def test_pipeline_validation_issues_completed():
    """Test when validation runs but flags issues (is_valid=False)"""
    pipeline = DocumentProcessingPipelineForTest("test_docs/validation_issues.pdf", "validation_issues.pdf", ".pdf")
    # Ensure OCR, classification, extraction succeed. Validation returns is_valid=False
    pipeline.textract_client.extract_text = lambda x: "Factura content here." # Classifier returns "factura"
    # MockDocumentProcessor for "factura" returns generic_field, and its validator returns is_valid=False

    result = pipeline.run()
    assert result.metadata.processing_status == "completed_with_validation_issues"
    assert result.extracted_data is not None
    assert result.extracted_data.document_type == "factura"
    assert result.validation_result is not None
    assert result.validation_result.is_valid is False
    assert len(mock_stored_data) == 1

if __name__ == '__main__':
    pytest.main([__file__])
