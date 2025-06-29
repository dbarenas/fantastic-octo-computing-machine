# Flujo de procesamiento del documento
# This module defines the `DocumentProcessingPipeline` class, which orchestrates
# the end-to-end processing of a single document. The typical workflow is:
#
# 1.  **Initialization**: The pipeline is instantiated with paths/info for a document.
# 2.  **OCR (Text Extraction)**: Raw text is extracted from the document image/PDF.
#     (e.g., using `utils.textract_utils.TextractClient`).
# 3.  **Classification**: The extracted text is analyzed to determine the document type
#     (e.g., "factura", "certificado_final") using `classifier.DocumentClassifier`.
# 4.  **Processor Selection**: Based on the classified document type, a specific
#     processor (containing an extractor and a validator) is retrieved using
#     `processor_factory.get_processor`.
# 5.  **Data Extraction**: The selected extractor pulls specific fields from the raw text.
# 6.  **Data Validation**: The extracted fields are validated against business rules
#     by the selected validator.
# 7.  **Storage**: The original document metadata, raw text (or its path),
#     extracted data, and validation results are stored in a database
#     (e.g., using functions from `db.insert`).
# 8.  **Output**: The pipeline returns a structured representation of the processed
#     document (e.g., a `ProcessedDocument` Pydantic model).
#
# This processed data can then be queried via the API or used by the RAG system.

# from utils.textract_utils import TextractClient # Assuming Textract client
# from classifier import DocumentClassifier
# from processor_factory import get_processor
# from db.insert import store_document_data # Assuming DB insert functions
# from models import ProcessedDocument, DocumentMetadata, ExtractedData, ValidationResult # Pydantic models
# import uuid
# from datetime import datetime
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

class DocumentProcessingPipeline:
    def __init__(self, document_path: str, file_name: str, file_type: str):
        self.document_path = document_path # Could be a local path or S3 URI
        self.file_name = file_name
        self.file_type = file_type
        self.document_id = str(uuid.uuid4())

        # Initialize clients and components (these would be properly initialized with config)
        # self.textract_client = TextractClient()
        # self.db_inserter = ... # Instance for DB operations

        self.metadata = DocumentMetadata(
            document_id=self.document_id,
            file_name=self.file_name,
            file_type=self.file_type,
            upload_date=datetime.now(),
            processing_status="pending"
        )
        self.raw_text = None
        self.extracted_data_model = None
        self.validation_result_model = None


    def run(self) -> ProcessedDocument:
        """
        Executes the full document processing pipeline.
        """
        logger.info(f"Starting processing for document: {self.file_name} (ID: {self.document_id})")
        self.metadata.processing_status = "processing_ocr"
        # 1. Extract text using OCR (e.g., AWS Textract)
        #    This is a placeholder. Actual implementation will call Textract.
        #    self.raw_text = self.textract_client.extract_text(self.document_path)
        self.raw_text = f"Simulated extracted text for {self.file_name}. Contenido del documento..."
        if not self.raw_text:
            logger.error(f"OCR failed for {self.document_id}")
            self.metadata.processing_status = "error_ocr"
            self.metadata.error_message = "OCR failed or document is empty."
            # self.store_initial_status() # Store error status
            return self._build_processed_document()

        logger.info(f"OCR successful for {self.document_id}. Text length: {len(self.raw_text)}")
        self.metadata.processing_status = "processing_classification"

        # 2. Classify document type
        # classifier = DocumentClassifier(self.raw_text)
        # doc_type = classifier.classify()
        doc_type = "simulated_doc_type" # Placeholder
        if not doc_type:
            logger.warning(f"Could not classify document {self.document_id}")
            self.metadata.processing_status = "error_classification"
            self.metadata.error_message = "Document type could not be determined."
            # self.store_classification_failure()
            return self._build_processed_document()

        logger.info(f"Document {self.document_id} classified as: {doc_type}")
        self.metadata.processing_status = "processing_extraction"

        # 3. Get appropriate processor (extractor & validator) using Factory
        # processor = get_processor(doc_type, self.raw_text) # from processor_factory.py
        # if not processor:
        #     logger.error(f"No processor found for document type: {doc_type} (ID: {self.document_id})")
        #     self.metadata.processing_status = "error_no_processor"
        #     self.metadata.error_message = f"No processor available for document type '{doc_type}'."
        #     # self.store_processor_failure()
        #     return self._build_processed_document()

        # Placeholder for processor
        class MockProcessor:
            def __init__(self, text, doc_type_name):
                self.text = text
                self.doc_type_name = doc_type_name
            def extract(self): return {"sim_field_1": "value1", "doc_type": self.doc_type_name}
            def validate(self, data): return {"is_valid": True, "details": {"sim_check": "passed"}}

        processor = MockProcessor(self.raw_text, doc_type)


        # 4. Extract data
        try:
            extracted_fields = processor.extract()
            self.extracted_data_model = ExtractedData(document_type=doc_type, fields=extracted_fields)
            logger.info(f"Data extracted for {self.document_id}: {extracted_fields}")
            self.metadata.processing_status = "processing_validation"
        except Exception as e:
            logger.error(f"Error during data extraction for {self.document_id} ({doc_type}): {e}", exc_info=True)
            self.metadata.processing_status = "error_extraction"
            self.metadata.error_message = f"Extraction failed: {str(e)}"
            # self.store_extraction_failure()
            return self._build_processed_document()

        # 5. Validate data
        try:
            validation_output = processor.validate(self.extracted_data_model.fields)
            self.validation_result_model = ValidationResult(**validation_output)
            logger.info(f"Data validated for {self.document_id}: {self.validation_result_model.is_valid}")
            self.metadata.processing_status = "completed" if self.validation_result_model.is_valid else "completed_with_validation_issues"
        except Exception as e:
            logger.error(f"Error during data validation for {self.document_id} ({doc_type}): {e}", exc_info=True)
            self.metadata.processing_status = "error_validation"
            self.metadata.error_message = f"Validation failed: {str(e)}"
            # self.store_validation_failure()
            return self._build_processed_document()

        # 6. Store results in DB
        # result_to_store = self._build_processed_document()
        # store_document_data(result_to_store) # This would interact with db/insert.py
        logger.info(f"Processing complete for {self.document_id}. Final status: {self.metadata.processing_status}")

        return self._build_processed_document()

    def _build_processed_document(self) -> ProcessedDocument:
        return ProcessedDocument(
            metadata=self.metadata,
            raw_text=self.raw_text,
            extracted_data=self.extracted_data_model,
            validation_result=self.validation_result_model
        )

if __name__ == "__main__":
    # This is a mock execution.
    # In a real scenario, this would be triggered by main.py or an API call.
    print("Simulating document processing pipeline run...")
    # Note: The following lines are commented out as they depend on external files/config
    # and actual document paths that don't exist in this sandboxed environment.
    # from models import ProcessedDocument, DocumentMetadata, ExtractedData, ValidationResult
    # import uuid
    # from datetime import datetime
    # import logging
    # logging.basicConfig(level="INFO")
    # logger = logging.getLogger(__name__)

    # pipeline_instance = DocumentProcessingPipeline(
    # document_path="dummy_document.pdf", # Path to the document
    # file_name="dummy_document.pdf",
    # file_type="pdf"
    # )
    # result = pipeline_instance.run()
    # print(f"Pipeline finished. Document ID: {result.metadata.document_id}, Status: {result.metadata.processing_status}")
    # if result.extracted_data:
    # print(f"Extracted data: {result.extracted_data.fields}")
    # if result.validation_result:
    # print(f"Validation result: {result.validation_result.is_valid}, Details: {result.validation_result.details}")
    pass
