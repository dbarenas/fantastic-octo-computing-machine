from base.base_validator import BaseValidator
from datetime import datetime

class CertificadoFinalValidator(BaseValidator):
    def validate(self) -> dict:
        results = {
            "firmas_presentes": self.data.get("firmas", False),
            "fecha_valida": self._validar_fecha(self.data.get("fecha")),
            "tiene_observaciones": self.data.get("observaciones", False)
        }
        results["valido"] = all([results["firmas_presentes"], results["fecha_valida"]])
        return results

    def _validar_fecha(self, fecha_str):
        if not fecha_str:
            return False
        try:
            fecha = datetime.strptime(fecha_str, "%d/%m/%Y")
            # Example validation: date should be before June 30, 2026
            return fecha < datetime(2026, 6, 30)
        except ValueError:
            return False
