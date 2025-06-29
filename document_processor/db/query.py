# Funciones para consultas a la base de datos

# from .database import get_db_session # For SQLAlchemy
# from .models_orm import DocumentModel, ExtractedDataModel, ValidationResultModel # SQLAlchemy ORM Models
# from models import ProcessedDocument, DocumentMetadata, ExtractedData, ValidationResult # Pydantic models
# from sqlalchemy.orm import joinedload
# import json
# from typing import Optional, List

# --- SQLAlchemy Example (if chosen) ---
# def get_document_by_id_orm(db_session, doc_id: str) -> Optional[ProcessedDocument]:
#     """
#     Retrieves a fully populated ProcessedDocument object by its ID using SQLAlchemy ORM.
#     """
#     db_doc = db_session.query(DocumentModel)\
#         .options(
#             joinedload(DocumentModel.extracted_data_relation), # Eager load related data
#             joinedload(DocumentModel.validation_result_relation)
#         )\
#         .filter(DocumentModel.id == doc_id).first()

#     if not db_doc:
#         return None

#     # Reconstruct Pydantic models from ORM objects
#     metadata = DocumentMetadata(
#         document_id=db_doc.id,
#         file_name=db_doc.file_name,
#         file_type=db_doc.file_type,
#         upload_date=db_doc.upload_timestamp,
#         processing_status=db_doc.processing_status,
#         error_message=db_doc.error_message
#     )
#     extracted_data = None
#     if db_doc.extracted_data_relation:
#         extracted_data = ExtractedData(
#             document_type=db_doc.document_type_classified, # Assuming this is stored in DocumentModel
#             fields=json.loads(db_doc.extracted_data_relation.data_json)
#         )
#     validation_result = None
#     if db_doc.validation_result_relation:
#         validation_result = ValidationResult(
#             is_valid=db_doc.validation_result_relation.is_overall_valid,
#             details=json.loads(db_doc.validation_result_relation.results_json)
#         )

#     # raw_text would need to be fetched if stored separately (e.g., from raw_text_path)
#     # For this example, assuming it's not directly part of this query for simplicity.

#     return ProcessedDocument(
#         metadata=metadata,
#         extracted_data=extracted_data,
#         validation_result=validation_result
#         # raw_text should be populated if applicable
#     )

# def find_documents_orm(db_session, status: Optional[str] = None, doc_type: Optional[str] = None) -> List[ProcessedDocument]:
#     """
#     Finds documents based on status or document type using SQLAlchemy ORM.
#     Returns a list of ProcessedDocument objects.
#     """
#     query = db_session.query(DocumentModel)\
#         .options(
#             joinedload(DocumentModel.extracted_data_relation),
#             joinedload(DocumentModel.validation_result_relation)
#         )

#     if status:
#         query = query.filter(DocumentModel.processing_status == status)
#     if doc_type:
#         query = query.filter(DocumentModel.document_type_classified == doc_type)

#     db_docs = query.all()
#     processed_docs = []
#     for db_doc in db_docs:
#         # Reconstruct Pydantic models (similar to get_document_by_id_orm)
#         # This part can be refactored into a helper function _map_orm_to_pydantic(db_doc)
#         metadata = DocumentMetadata(...)
#         extracted_data = ExtractedData(...) if db_doc.extracted_data_relation else None
#         validation_result = ValidationResult(...) if db_doc.validation_result_relation else None
#         processed_docs.append(ProcessedDocument(metadata=metadata, extracted_data=extracted_data, validation_result=validation_result))
#     return processed_docs

# --- End SQLAlchemy Example ---


# --- Simpler SQLite3 example (without ORM) ---
from .database import get_db_connection # Uses the simple sqlite3 connection
# from models import ProcessedDocument, DocumentMetadata, ExtractedData, ValidationResult # Pydantic models
import json
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def get_document_details_by_id(doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves all details for a document (metadata, extracted data, validation results)
    from SQLite and returns them as a dictionary structured like ProcessedDocument Pydantic model.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch from documents table
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        doc_row = cursor.fetchone()

        if not doc_row:
            return None

        result = {
            "metadata": {
                "document_id": doc_row["id"],
                "file_name": doc_row["file_name"],
                "file_type": doc_row["file_type"],
                "upload_date": doc_row["upload_timestamp"], # SQLite stores as TEXT, Pydantic model expects datetime
                "processing_status": doc_row["processing_status"],
                "error_message": doc_row["error_message"]
            },
            "extracted_data": None,
            "validation_result": None,
            "raw_text": None # Placeholder, assuming raw text might be loaded from raw_text_path
        }

        # If raw text is stored in a file, its path would be doc_row["raw_text_path"]
        # Here you could add logic to load it if needed.

        # Fetch from extracted_data table
        cursor.execute("SELECT data_json FROM extracted_data WHERE document_id = ?", (doc_id,))
        extracted_row = cursor.fetchone()
        if extracted_row and extracted_row["data_json"]:
            result["extracted_data"] = {
                "document_type": doc_row["document_type_classified"], # From the main 'documents' table
                "fields": json.loads(extracted_row["data_json"])
            }

        # Fetch from validation_results table
        cursor.execute("SELECT is_overall_valid, results_json FROM validation_results WHERE document_id = ?", (doc_id,))
        validation_row = cursor.fetchone()
        if validation_row:
            result["validation_result"] = {
                "is_valid": bool(validation_row["is_overall_valid"]),
                "details": json.loads(validation_row["results_json"]) if validation_row["results_json"] else {}
            }

        return result # This dict should be parseable by ProcessedDocument(**result)

    except Exception as e:
        logger.error(f"Error fetching document details for ID {doc_id} from SQLite: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def find_documents(status: Optional[str] = None, doc_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Finds documents based on status or classified document type from SQLite.
    Returns a list of document metadata dictionaries.
    For full details, one would then call get_document_details_by_id for each.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT id, file_name, processing_status, document_type_classified, upload_timestamp FROM documents WHERE 1=1"
        params = []

        if status:
            query += " AND processing_status = ?"
            params.append(status)
        if doc_type:
            query += " AND document_type_classified = ?"
            params.append(doc_type)

        query += " ORDER BY upload_timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()

        documents_summary = []
        for row in rows:
            documents_summary.append(dict(row)) # Convert sqlite3.Row to dict
        return documents_summary

    except Exception as e:
        logger.error(f"Error finding documents in SQLite: {e}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()

# Example usage (simulation)
if __name__ == '__main__':
    # Requires database.py to have run initialize_database() and insert.py to have added data
    # from document_processor.db.database import initialize_database
    # from document_processor.db.insert import store_document_data # To add some test data
    # from document_processor.models import ProcessedDocument, DocumentMetadata, ExtractedData, ValidationResult # For creating test data
    # from datetime import datetime

    # print("Initializing DB for query example...")
    # initialize_database()

    # # Add some test data if it doesn't exist (using the dict structure expected by store_document_data)
    # test_doc_1_data = {
    #     "metadata": {
    #         "document_id": "query_test_doc_001", "file_name": "q_test1.pdf", "file_type": ".pdf",
    #         "upload_date": datetime.now().isoformat(), "processing_status": "completed",
    #         "error_message": None
    #     },
    #     "extracted_data": {"document_type": "factura", "fields": {"total": 250, "cliente": "Cliente A"}},
    #     "validation_result": {"is_valid": True, "details": {"check1": "ok"}},
    #     "raw_text_path": "/path/to/raw_text_for_query_test_doc_001.txt" # Example path
    # }
    # test_doc_2_data = {
    #     "metadata": {
    #         "document_id": "query_test_doc_002", "file_name": "q_test2.png", "file_type": ".png",
    #         "upload_date": datetime.now().isoformat(), "processing_status": "error_validation",
    #         "error_message": "Date format incorrect"
    #     },
    #     "extracted_data": {"document_type": "certificado_final", "fields": {"fecha": "2023/13/01"}}, # Invalid date
    #     "validation_result": {"is_valid": False, "details": {"date_check": "failed"}},
    # }
    # store_document_data(test_doc_1_data)
    # store_document_data(test_doc_2_data)

    # print("\n--- Testing get_document_details_by_id ---")
    # doc1_details = get_document_details_by_id("query_test_doc_001")
    # if doc1_details:
    #     print(f"Details for query_test_doc_001: {json.dumps(doc1_details, indent=2)}")
    #     # Example: Reconstruct Pydantic model (if models.py is in PYTHONPATH)
    #     # pydantic_doc = ProcessedDocument(**doc1_details)
    #     # print(f"Pydantic model for doc1: {pydantic_doc.metadata.file_name}")
    # else:
    #     print("Document query_test_doc_001 not found.")

    # doc_nonexistent = get_document_details_by_id("non_existent_doc")
    # if not doc_nonexistent:
    #     print("Correctly did not find non_existent_doc.")

    # print("\n--- Testing find_documents ---")
    # completed_docs = find_documents(status="completed")
    # print(f"Found {len(completed_docs)} 'completed' documents:")
    # for doc_summary in completed_docs:
    #     print(f"  - ID: {doc_summary['id']}, Name: {doc_summary['file_name']}")

    # factura_docs = find_documents(doc_type="factura")
    # print(f"\nFound {len(factura_docs)} 'factura' documents:")
    # for doc_summary in factura_docs:
    #     print(f"  - ID: {doc_summary['id']}, Name: {doc_summary['file_name']}")

    # all_docs = find_documents(limit=5)
    # print(f"\nFound {len(all_docs)} documents (limit 5):")
    # for doc_summary in all_docs:
    #     print(f"  - ID: {doc_summary['id']}, Name: {doc_summary['file_name']}, Status: {doc_summary['processing_status']}")
    pass
