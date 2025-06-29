# Funciones para inserciones en la base de datos

# from .database import get_db_session # For SQLAlchemy
# from .models_orm import DocumentModel, ExtractedDataModel, ValidationResultModel # SQLAlchemy ORM Models
# from models import ProcessedDocument # Pydantic model from the main project structure
# from datetime import datetime
# import json

# --- SQLAlchemy Example (if chosen) ---
# def store_processed_document_orm(db_session, processed_doc: ProcessedDocument):
#     """
#     Stores the entire ProcessedDocument object into the database using SQLAlchemy ORM.
#     """
#     try:
#         # Create DocumentModel instance
#         db_doc = DocumentModel(
#             id=processed_doc.metadata.document_id,
#             file_name=processed_doc.metadata.file_name,
#             file_type=processed_doc.metadata.file_type,
#             upload_timestamp=processed_doc.metadata.upload_date,
#             processing_status=processed_doc.metadata.processing_status,
#             document_type_classified=processed_doc.extracted_data.document_type if processed_doc.extracted_data else None,
#             # raw_text_path might be set if raw_text is stored in a file
#             error_message=processed_doc.metadata.error_message,
#             last_updated_timestamp=datetime.now()
#         )
#         db_session.add(db_doc)

#         # Create ExtractedDataModel instance (if data was extracted)
#         if processed_doc.extracted_data and processed_doc.extracted_data.fields:
#             db_extracted_data = ExtractedDataModel(
#                 document_id=processed_doc.metadata.document_id,
#                 data_json=json.dumps(processed_doc.extracted_data.fields)
#             )
#             db_session.add(db_extracted_data)

#         # Create ValidationResultModel instance (if validation was performed)
#         if processed_doc.validation_result:
#             db_validation_result = ValidationResultModel(
#                 document_id=processed_doc.metadata.document_id,
#                 is_overall_valid=processed_doc.validation_result.is_valid,
#                 results_json=json.dumps(processed_doc.validation_result.details)
#             )
#             db_session.add(db_validation_result)

#         db_session.commit()
#         db_session.refresh(db_doc) # Refresh to get any DB-generated fields
#         # logger.info(f"Document {processed_doc.metadata.document_id} and its data stored successfully.")
#         return db_doc
#     except Exception as e:
#         db_session.rollback()
#         # logger.error(f"Error storing document {processed_doc.metadata.document_id}: {e}", exc_info=True)
#         raise
# --- End SQLAlchemy Example ---


# --- Simpler SQLite3 example (without ORM) ---
from .database import get_db_connection # Uses the simple sqlite3 connection
# from models import ProcessedDocument # Pydantic model from main project
from datetime import datetime
import json
import logging # For logging potential errors

logger = logging.getLogger(__name__)

def store_document_data(processed_doc_data: dict): # Assuming processed_doc_data is a dict representation
    """
    Stores document metadata, extracted data, and validation results
    into respective SQLite tables.
    `processed_doc_data` should be a dictionary mirroring `ProcessedDocument` Pydantic model.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        metadata = processed_doc_data.get("metadata", {})
        doc_id = metadata.get("document_id")

        if not doc_id:
            logger.error("Cannot store document data: document_id is missing.")
            return False

        # Upsert into 'documents' table (Insert or Replace)
        cursor.execute("""
            INSERT OR REPLACE INTO documents (
                id, file_name, file_type, upload_timestamp,
                processing_status, document_type_classified,
                raw_text_path, error_message, last_updated_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc_id,
            metadata.get("file_name"),
            metadata.get("file_type"),
            metadata.get("upload_date", datetime.now().isoformat()), # Ensure upload_date is string
            metadata.get("processing_status"),
            processed_doc_data.get("extracted_data", {}).get("document_type") if processed_doc_data.get("extracted_data") else None,
            processed_doc_data.get("raw_text_path"), # Path if raw text is stored separately
            metadata.get("error_message"),
            datetime.now().isoformat()
        ))

        # Upsert into 'extracted_data' table
        extracted_data = processed_doc_data.get("extracted_data")
        if extracted_data and extracted_data.get("fields"):
            cursor.execute("""
                INSERT OR REPLACE INTO extracted_data (document_id, data_json)
                VALUES (?, ?)
            """, (doc_id, json.dumps(extracted_data.get("fields"))))

        # Upsert into 'validation_results' table
        validation_result = processed_doc_data.get("validation_result")
        if validation_result:
            cursor.execute("""
                INSERT OR REPLACE INTO validation_results (document_id, is_overall_valid, results_json)
                VALUES (?, ?, ?)
            """, (
                doc_id,
                1 if validation_result.get("is_valid") else 0,
                json.dumps(validation_result.get("details"))
            ))

        conn.commit()
        logger.info(f"Data for document ID {doc_id} stored/updated successfully in SQLite.")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error storing data for document ID {doc_id} in SQLite: {e}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()

# Example usage (simulation - ProcessedDocument Pydantic model would be used in practice)
if __name__ == '__main__':
    # This requires models.py to be accessible and database.py to have run initialize_database()
    # from document_processor.models import ProcessedDocument, DocumentMetadata, ExtractedData, ValidationResult
    # from document_processor.db.database import initialize_database

    # print("Initializing DB for insert example...")
    # initialize_database() # Make sure tables exist

    # mock_metadata = DocumentMetadata(
    #     document_id="test_doc_002",
    #     file_name="test_file_002.pdf",
    #     file_type=".pdf",
    #     upload_date=datetime.now(),
    #     processing_status="completed"
    # )
    # mock_extracted = ExtractedData(
    #     document_type="factura",
    #     fields={"total": 100, "iva": 21, "fecha": "2023-03-03"}
    # )
    # mock_validation = ValidationResult(
    #     is_valid=True,
    #     details={"total_check": "passed", "date_check": "passed"}
    # )
    # mock_processed_doc = ProcessedDocument(
    #     metadata=mock_metadata,
    #     extracted_data=mock_extracted,
    #     validation_result=mock_validation,
    #     raw_text="This is the raw text of the document." # raw_text_path would be set if stored in file
    # )

    # print(f"\nAttempting to store mock document: {mock_processed_doc.metadata.document_id}")
    # success = store_document_data(mock_processed_doc.model_dump()) # Convert Pydantic to dict for this function

    # if success:
    #     print(f"Mock document {mock_processed_doc.metadata.document_id} data insertion attempt successful.")
    # else:
    #     print(f"Mock document {mock_processed_doc.metadata.document_id} data insertion attempt failed.")

    # # Test storing a document with an error
    # mock_metadata_error = DocumentMetadata(
    #     document_id="error_doc_001",
    #     file_name="error_file_001.txt",
    #     file_type=".txt",
    #     upload_date=datetime.now(),
    #     processing_status="error_ocr",
    #     error_message="OCR failed due to unsupported format."
    # )
    # mock_processed_doc_error = ProcessedDocument(
    #     metadata=mock_metadata_error
    # )
    # print(f"\nAttempting to store mock error document: {mock_processed_doc_error.metadata.document_id}")
    # success_error = store_document_data(mock_processed_doc_error.model_dump())
    # if success_error:
    #     print(f"Mock error document {mock_processed_doc_error.metadata.document_id} data insertion attempt successful.")
    # else:
    #     print(f"Mock error document {mock_processed_doc_error.metadata.document_id} data insertion attempt failed.")
    pass
