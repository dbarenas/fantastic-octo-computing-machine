# Esquemas de datos y validaciones (Pydantic models for FastAPI, etc.)

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime

class DocumentMetadata(BaseModel):
    document_id: str
    file_name: str
    file_type: str # e.g., pdf, png, jpg
    upload_date: datetime
    processing_status: str # e.g., pending, processing, completed, error
    error_message: Optional[str] = None

class ExtractedData(BaseModel):
    document_type: str
    fields: Dict[str, Any] # Store extracted fields as a dictionary

class ValidationResult(BaseModel):
    is_valid: bool
    details: Dict[str, Any] # Detailed validation checks

class ProcessedDocument(BaseModel):
    metadata: DocumentMetadata
    extracted_data: Optional[ExtractedData] = None
    validation_result: Optional[ValidationResult] = None
    raw_text: Optional[str] = None # Store raw text from OCR

# Example for a specific document type if needed for API request/response
class CertificadoFinalData(BaseModel):
    firmas: bool
    fecha: Optional[str] # Assuming date as string for now, validation handled elsewhere
    observaciones: bool

    @validator('fecha')
    def validate_fecha_format(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%d/%m/%Y')
            except ValueError:
                raise ValueError('Fecha must be in DD/MM/YYYY format')
        return v

class APIStatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    document_id: Optional[str] = None

print("Data models defined.")
