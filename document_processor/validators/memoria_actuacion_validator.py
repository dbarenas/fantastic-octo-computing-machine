from base.base_validator import BaseValidator
from datetime import datetime

class MemoriaActuacionValidator(BaseValidator):
    def validate(self) -> dict:
        """
        Validates extracted data for "Memoria de Actuación" documents.
        This is a placeholder and needs to be implemented with actual
        validation logic for this document type.
        """
        results = {
            "titulo_presente": self.data.get("titulo_proyecto") is not None and len(self.data.get("titulo_proyecto", "")) > 5,
            "fecha_elaboracion_valida": self._validar_fecha_elaboracion(self.data.get("fecha_elaboracion")),
            "resumen_presente": self.data.get("resumen") is not None and len(self.data.get("resumen", "")) > 20,
            # Add more validation checks:
            # - Presupuesto (Budget) within a reasonable range (if extracted)
            # - Plazo de Ejecución (Execution Period) makes sense (if extracted)
            # - Consistency checks between different sections (if applicable)
        }

        # Overall validity (example: all key fields must be valid)
        results["valido"] = all([
            results["titulo_presente"],
            results["fecha_elaboracion_valida"],
            results["resumen_presente"]
        ])
        return results

    def _validar_fecha_elaboracion(self, fecha_str: str) -> bool:
        if not fecha_str:
            return False
        try:
            # Assuming date format DD/MM/YYYY or DD-MM-YYYY from extractor
            fecha = datetime.strptime(fecha_str.replace('-', '/'), "%d/%m/%Y")
            # Example rule: date cannot be too far in the past or in the future
            # For instance, not older than 5 years and not more than 1 year in the future.
            return (datetime.now().year - 5) <= fecha.year <= (datetime.now().year + 1)
        except ValueError:
            return False

if __name__ == '__main__':
    # Valid data
    valid_memoria_data = {
        "titulo_proyecto": "Desarrollo de Nueva Plataforma Digital",
        "fecha_elaboracion": "15/03/2024",
        "entidad_promotora": "Innovaciones Tech S.L.",
        "resumen": "El presente documento describe el plan de actuación para el desarrollo..."
    }
    validator_valid = MemoriaActuacionValidator(valid_memoria_data)
    result_valid = validator_valid.validate()
    print("Validation for Valid Memoria Data (Placeholder):")
    for key, value in result_valid.items():
        print(f"- {key}: {value}")

    # Invalid data: old date
    invalid_memoria_data_date = {
        "titulo_proyecto": "Proyecto Histórico",
        "fecha_elaboracion": "01/01/2010", # Too old
        "resumen": "Un proyecto realizado hace mucho tiempo."
    }
    validator_invalid_date = MemoriaActuacionValidator(invalid_memoria_data_date)
    result_invalid_date = validator_invalid_date.validate()
    print("\nValidation for Invalid Memoria Data (Old Date):")
    for key, value in result_invalid_date.items():
        print(f"- {key}: {value}")

    # Invalid data: missing title
    invalid_memoria_data_title = {
        "titulo_proyecto": None, # Missing title
        "fecha_elaboracion": "10/02/2024",
        "resumen": "Descripción de un proyecto sin título."
    }
    validator_invalid_title = MemoriaActuacionValidator(invalid_memoria_data_title)
    result_invalid_title = validator_invalid_title.validate()
    print("\nValidation for Invalid Memoria Data (Missing Title):")
    for key, value in result_invalid_title.items():
        print(f"- {key}: {value}")

    # Invalid data: short resumen
    invalid_memoria_data_resumen = {
        "titulo_proyecto": "Proyecto Breve",
        "fecha_elaboracion": "11/02/2024",
        "resumen": "Corto." # Resumen too short
    }
    validator_invalid_resumen = MemoriaActuacionValidator(invalid_memoria_data_resumen)
    result_invalid_resumen = validator_invalid_resumen.validate()
    print("\nValidation for Invalid Memoria Data (Short Resumen):")
    for key, value in result_invalid_resumen.items():
        print(f"- {key}: {value}")
