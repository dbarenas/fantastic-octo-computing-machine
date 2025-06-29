from document_processor.base.base_extractor import BaseExtractor
import re

class CertificadoFinalExtractor(BaseExtractor):
    def __init__(self, bucket_name: str, document_key: str):
        super().__init__(bucket_name, document_key)

    def extract(self) -> dict:
        return {
            "firmas": self._extraer_firmas(),
            "fecha": self._extraer_fecha(),
            "observaciones": self._extraer_observaciones()
        }

    def _extraer_firmas(self):
        return "director de obra" in self.text.lower() and "director de ejecución" in self.text.lower()

    def _extraer_fecha(self):
        match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", self.text)
        return match.group(1) if match else None

    def _extraer_observaciones(self):
        return "observaciones" in self.text.lower() or "reparos" in self.text.lower()
