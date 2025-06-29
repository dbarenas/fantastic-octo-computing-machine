import pytest
from unittest.mock import patch
from document_processor.extractors.certificado_final import CertificadoFinalExtractor
from document_processor.validators.certificado_final_validator import CertificadoFinalValidator

example_text = """
    Certificado Final de Obra
    Firmado por el Director de Obra y Director de Ejecución
    Fecha: 15/05/2025
    Sin observaciones.
"""

@patch('document_processor.base.base_extractor.extract_text_from_document')
def test_extractor(mock_extract_text):
    mock_extract_text.return_value = example_text
    extractor = CertificadoFinalExtractor(bucket_name="test-bucket", document_key="test-key.pdf")
    result = extractor.extract()
    assert result["firmas"] is True
    assert result["fecha"] == "15/05/2025"
    assert result["observaciones"] is True
    mock_extract_text.assert_called_once_with("test-bucket", "test-key.pdf", "us-east-1")

def test_validator_valid_data():
    data = {
        "firmas": True,
        "fecha": "15/05/2025",
        "observaciones": True
    }
    validator = CertificadoFinalValidator(data)
    result = validator.validate()
    assert result["firmas_presentes"] is True
    assert result["fecha_valida"] is True
    assert result["valido"] is True
    assert result["tiene_observaciones"] is True

def test_validator_invalid_date():
    data = {
        "firmas": True,
        "fecha": "15/07/2027", # Invalid date based on validator logic
        "observaciones": False
    }
    validator = CertificadoFinalValidator(data)
    result = validator.validate()
    assert result["firmas_presentes"] is True
    assert result["fecha_valida"] is False
    assert result["valido"] is False
    assert result["tiene_observaciones"] is False

def test_validator_missing_firmas():
    data = {
        "firmas": False,
        "fecha": "10/01/2024",
        "observaciones": True
    }
    validator = CertificadoFinalValidator(data)
    result = validator.validate()
    assert result["firmas_presentes"] is False
    assert result["fecha_valida"] is True
    assert result["valido"] is False # Valido depends on firmas_presentes and fecha_valida
    assert result["tiene_observaciones"] is True

def test_validator_invalid_date_format():
    data = {
        "firmas": True,
        "fecha": "2025-05-15", # Invalid date format
        "observaciones": False
    }
    validator = CertificadoFinalValidator(data)
    result = validator.validate()
    assert result["firmas_presentes"] is True
    assert result["fecha_valida"] is False
    assert result["valido"] is False
    assert result["tiene_observaciones"] is False

def test_validator_no_date():
    data = {
        "firmas": True,
        "fecha": None,
        "observaciones": False
    }
    validator = CertificadoFinalValidator(data)
    result = validator.validate()
    assert result["firmas_presentes"] is True
    assert result["fecha_valida"] is False
    assert result["valido"] is False
    assert result["tiene_observaciones"] is False
