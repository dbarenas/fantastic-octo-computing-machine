# Selecciona extractor y validador según tipo de documento

# from extractors.certificado_final import CertificadoFinalExtractor
# from validators.certificado_final_validator import CertificadoFinalValidator
# from extractors.facturas import FacturaExtractor # Assuming it exists
# from validators.facturas_validator import FacturaValidator # Assuming it exists
# from extractors.memoria_actuacion import MemoriaActuacionExtractor # Assuming it exists
# from validators.memoria_actuacion_validator import MemoriaActuacionValidator # Assuming it exists
# ... import other extractors and validators for all 12 types

# from base.base_extractor import BaseExtractor
# from base.base_validator import BaseValidator
# from typing import Optional, Type
# import logging

# logger = logging.getLogger(__name__)

# Placeholder for actual Extractor/Validator classes
# These would be imported from their respective modules
class BaseExtractor:
    def __init__(self, text): self.text = text
    def extract(self): raise NotImplementedError
class BaseValidator:
    def __init__(self, data): self.data = data
    def validate(self): raise NotImplementedError

class CertificadoFinalExtractor(BaseExtractor):
    def extract(self): return {"type": "CertificadoFinal", "extracted_field": "CF data"}
class CertificadoFinalValidator(BaseValidator):
    def validate(self): return {"is_valid": True, "validated_field": "CF valid"}

class FacturaExtractor(BaseExtractor):
    def extract(self): return {"type": "Factura", "extracted_field": "Factura data"}
class FacturaValidator(BaseValidator):
    def validate(self): return {"is_valid": True, "validated_field": "Factura valid"}

# ... define mock extractors/validators for other types up to 12

PROCESSOR_MAPPING = {
    "certificado_final": {
        "extractor": CertificadoFinalExtractor,
        "validator": CertificadoFinalValidator,
    },
    "factura": {
        "extractor": FacturaExtractor, # Placeholder, to be implemented
        "validator": FacturaValidator, # Placeholder, to be implemented
    },
    "memoria_actuacion": {
        # "extractor": MemoriaActuacionExtractor, # Placeholder
        # "validator": MemoriaActuacionValidator, # Placeholder
    },
    # ... Add mappings for all 12 document types
    # "document_type_3": {
    # "extractor": DocumentType3Extractor,
    # "validator": DocumentType3Validator,
    # },
    # ...
    # "document_type_12": {
    # "extractor": DocumentType12Extractor,
    # "validator": DocumentType12Validator,
    # },
}


class DocumentProcessor:
    """
    A wrapper class that holds both an extractor and a validator for a given document type.
    """
    def __init__(self, extractor_class: Type[BaseExtractor], validator_class: Type[BaseValidator], text: str):
        self.extractor = extractor_class(text)
        # Validator is instantiated later with extracted data
        self.validator_class = validator_class
        self.extracted_data = None

    def extract(self) -> dict:
        self.extracted_data = self.extractor.extract()
        return self.extracted_data

    def validate(self, data: Optional[dict] = None) -> dict:
        if data is None and self.extracted_data is None:
            raise ValueError("No data provided or extracted to validate.")
        data_to_validate = data if data is not None else self.extracted_data

        validator_instance = self.validator_class(data_to_validate)
        return validator_instance.validate()


def get_processor(document_type: str, text: str) -> Optional[DocumentProcessor]:
    """
    Factory function to get the appropriate processor (extractor and validator pair)
    for a given document type.
    """
    # logger.info(f"Attempting to get processor for document type: {document_type}")
    processor_config = PROCESSOR_MAPPING.get(document_type.lower())

    if processor_config:
        extractor_cls = processor_config.get("extractor")
        validator_cls = processor_config.get("validator")

        if extractor_cls and validator_cls:
            # logger.info(f"Found processor for {document_type}.")
            return DocumentProcessor(extractor_cls, validator_cls, text)
        else:
            # logger.warning(f"Incomplete processor configuration for type: {document_type}. Missing extractor or validator.")
            pass
    else:
        # logger.warning(f"No processor configuration found for document type: {document_type}")
        pass
    return None

if __name__ == '__main__':
    sample_text_cf = "Certificado Final de Obra. Director: Juan. Fecha: 01/01/2023"
    processor_cf = get_processor("certificado_final", sample_text_cf)
    if processor_cf:
        extracted = processor_cf.extract()
        print(f"Extracted CF: {extracted}")
        validated = processor_cf.validate()
        print(f"Validated CF: {validated}")
    else:
        print("Certificado Final processor not found.")

    sample_text_factura = "Factura No. 123. Total: $500"
    processor_factura = get_processor("factura", sample_text_factura)
    if processor_factura:
        extracted = processor_factura.extract()
        print(f"Extracted Factura: {extracted}")
        validated = processor_factura.validate()
        print(f"Validated Factura: {validated}")
    else:
        print("Factura processor not found.")

    processor_unknown = get_processor("unknown_type", "Some random text")
    if not processor_unknown:
        print("Unknown type processor correctly not found.")
