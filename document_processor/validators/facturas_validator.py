from base.base_validator import BaseValidator
from datetime import datetime

class FacturaValidator(BaseValidator):
    def validate(self) -> dict:
        """
        Validates extracted data for invoices (facturas).
        This is a placeholder and needs to be implemented with actual
        validation logic for invoices.
        """
        results = {
            "numero_factura_presente": self.data.get("numero_factura") is not None,
            "fecha_emision_valida": self._validar_fecha_emision(self.data.get("fecha_emision")),
            "total_factura_valido": self._validar_total(self.data.get("total_factura")),
            # Add more validation checks:
            # - Consistency between line totals and grand total
            # - Valid NIF/CIF for sender/receiver (if extracted)
            # - VAT calculation correctness (if applicable and data available)
        }

        # Overall validity (example: all key fields must be valid)
        results["valido"] = all([
            results["numero_factura_presente"],
            results["fecha_emision_valida"],
            results["total_factura_valido"]
        ])
        return results

    def _validar_fecha_emision(self, fecha_str: str) -> bool:
        if not fecha_str:
            return False
        try:
            # Assuming date format DD/MM/YYYY or DD-MM-YYYY from extractor
            fecha = datetime.strptime(fecha_str.replace('-', '/'), "%d/%m/%Y")
            # Example rule: invoice date cannot be in the future
            return fecha <= datetime.now()
        except ValueError:
            return False

    def _validar_total(self, total_value) -> bool:
        if total_value is None: # Can be 0, but not None if extraction failed
            return False
        try:
            total = float(total_value)
            # Example rule: total must be a positive number (or zero for credit notes, adjust if needed)
            return total >= 0
        except (ValueError, TypeError):
            return False

if __name__ == '__main__':
    # Valid data
    valid_invoice_data = {
        "numero_factura": "F2023-001",
        "fecha_emision": "25/12/2023",
        "total_factura": 242.00,
        "emisor_nombre": "Proveedor Ejemplo S.L.",
        "receptor_nombre": "Comprador Test S.A."
    }
    validator_valid = FacturaValidator(valid_invoice_data)
    result_valid = validator_valid.validate()
    print("Validation for Valid Invoice Data (Placeholder):")
    for key, value in result_valid.items():
        print(f"- {key}: {value}")

    # Invalid data: future date
    invalid_invoice_data_date = {
        "numero_factura": "F2024-002",
        "fecha_emision": "25/12/2099", # Future date
        "total_factura": 150.00
    }
    validator_invalid_date = FacturaValidator(invalid_invoice_data_date)
    result_invalid_date = validator_invalid_date.validate()
    print("\nValidation for Invalid Invoice Data (Future Date):")
    for key, value in result_invalid_date.items():
        print(f"- {key}: {value}")

    # Invalid data: missing total
    invalid_invoice_data_total = {
        "numero_factura": "F2024-003",
        "fecha_emision": "01/01/2024",
        "total_factura": None # Missing total
    }
    validator_invalid_total = FacturaValidator(invalid_invoice_data_total)
    result_invalid_total = validator_invalid_total.validate()
    print("\nValidation for Invalid Invoice Data (Missing Total):")
    for key, value in result_invalid_total.items():
        print(f"- {key}: {value}")

    # Invalid data: negative total
    invalid_invoice_data_neg_total = {
        "numero_factura": "F2024-004",
        "fecha_emision": "02/01/2024",
        "total_factura": -50.00 # Negative total
    }
    validator_invalid_neg_total = FacturaValidator(invalid_invoice_data_neg_total)
    result_invalid_neg_total = validator_invalid_neg_total.validate()
    print("\nValidation for Invalid Invoice Data (Negative Total):")
    for key, value in result_invalid_neg_total.items():
        print(f"- {key}: {value}")
