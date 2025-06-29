import pytest
from extractors.certificado_final import CertificadoFinalExtractor
from validators.certificado_final_validator import CertificadoFinalValidator

example_text = """
    Certificado Final de Obra
    Firmado por el Director de Obra y Director de Ejecución
    Fecha: 15/05/2025
    Sin observaciones.
"""

def test_extractor():
    extractor = CertificadoFinalExtractor(example_text)
    result = extractor.extract()
    assert result["firmas"] is True
    assert result["fecha"] == "15/05/2025"
    assert result["observaciones"] is True

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
