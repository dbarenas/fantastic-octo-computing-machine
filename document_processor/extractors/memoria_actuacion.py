from document_processor.base.base_extractor import BaseExtractor
import re

class MemoriaActuacionExtractor(BaseExtractor):
    def __init__(self, bucket_name: str, document_key: str):
        super().__init__(bucket_name, document_key)

    def extract(self) -> dict:
        """
        Extracts information specific to "Memoria de Actuación" documents.
        This is a placeholder and needs to be implemented with actual
        extraction logic for this document type.

        Common fields might include:
        - Título del Proyecto/Actuación (Project/Action Title)
        - Fecha de Elaboración (Preparation Date)
        - Responsable/Técnico Redactor (Responsible Person/Technical Writer)
        - Entidad Promotora (Promoting Entity)
        - Presupuesto (Budget)
        - Plazo de Ejecución (Execution Period)
        - Resumen Ejecutivo (Executive Summary)
        - Objetivos (Objectives)
        - Descripción de la Actuación (Description of Action)
        - Resultados Esperados/Obtenidos (Expected/Obtained Results)
        """
        # Placeholder logic:
        return {
            "titulo_proyecto": self._extraer_titulo(),
            "fecha_elaboracion": self._extraer_fecha(),
            "entidad_promotora": "Placeholder Entidad", # Placeholder
            "resumen": self._extraer_resumen() # Placeholder
        }

    def _extraer_titulo(self):
        # Example: search for lines starting with "Título:", "Proyecto:", "Actuación:"
        match = re.search(r"^(?:Título del Proyecto|Proyecto|Actuación)[:\s]*(.+)$", self.text, re.IGNORECASE | re.MULTILINE)
        return match.group(1).strip() if match else None

    def _extraer_fecha(self):
        # Example: search for "Fecha de Elaboración:" or a date near the title
        match = re.search(r"(?:Fecha de Elaboración|Fecha)[:\s]*(\d{2}[-/]\d{2}[-/]\d{4})", self.text, re.IGNORECASE)
        return match.group(1) if match else None

    def _extraer_resumen(self):
        # Example: look for a section titled "Resumen Ejecutivo" or "Resumen"
        # This is complex as it might span multiple paragraphs.
        # A simple approach might be to capture text after a "Resumen" heading.
        match = re.search(r"(?:Resumen Ejecutivo|Resumen)\s*[:\n](.*?)(?:\n\n\w+[:\n]|\Z)", self.text, re.IGNORECASE | re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()[:500] + "..." # Return a snippet
        return "Resumen no encontrado o lógica no implementada."


if __name__ == '__main__':
    sample_memoria_text = """
    MEMORIA DE ACTUACIÓN

    Título del Proyecto: Desarrollo de Nueva Plataforma Digital
    Fecha de Elaboración: 15/03/2024
    Entidad Promotora: Innovaciones Tech S.L.

    Resumen Ejecutivo:
    El presente documento describe el plan de actuación para el desarrollo
    de una nueva plataforma digital destinada a mejorar la interacción con
    nuestros clientes. Se detallan los objetivos, fases y presupuesto.

    1. Introducción
    ...
    """
    # The __main__ block needs to be updated or removed as it relies on old constructor
    # For now, let's comment it out or adapt it if we have sample S3 documents.
    # extractor = MemoriaActuacionExtractor("some-bucket", "some-key/sample_memoria_text.pdf")
    # data = extractor.extract()
    # print("Extracted Memoria de Actuación Data (Placeholder):")
    # for key, value in data.items():
    #     print(f"- {key}: {value}")

    # sample_memoria_text_2 = """
    # Proyecto: Mejora Eficiencia Energética
    # Fecha: 01/02/2023

    # Resumen
    # Este proyecto busca reducir el consumo energético en un 20%.
    # Se implementarán nuevas tecnologías y se optimizarán procesos.
    # """
    # extractor_2 = MemoriaActuacionExtractor("some-bucket", "some-key/sample_memoria_text_2.pdf")
    # data_2 = extractor_2.extract()
    # print("\nExtracted Memoria de Actuación Data 2 (Placeholder):")
    # for key, value in data_2.items():
    #     print(f"- {key}: {value}")
    print("MemoriaActuacionExtractor __main__ block needs update for S3 functionality.")
