import pytest
# from classifier import DocumentClassifier # Assuming classifier.py is in the same directory orPYTHONPATH

# --- Mock DocumentClassifier for testing purposes ---
# In a real scenario, you'd import the actual DocumentClassifier
from typing import Optional
class DocumentClassifier:
    def __init__(self, text: str):
        self.text = text.lower()

    def classify(self) -> Optional[str]:
        if "certificado final de obra" in self.text and "director de obra" in self.text:
            return "certificado_final"
        elif "factura nº" in self.text and "total:" in self.text:
            return "factura"
        elif "memoria de actuación" in self.text and "objetivos:" in self.text:
            return "memoria_actuacion"
        # Add more mock rules for other 9 document types if needed for comprehensive tests
        # elif "type_4_keyword" in self.text:
        #     return "document_type_4"
        # ...
        # elif "type_12_keyword" in self.text:
        #     return "document_type_12"
        return None
# --- End Mock DocumentClassifier ---

# Test cases: (text_input, expected_document_type)
test_data = [
    ("CERTIFICADO FINAL DE OBRA\nFirma del Director de Obra: ...", "certificado_final"),
    ("Factura Nº 12345\nCliente: Juan Pérez\nTotal: 100.00 EUR", "factura"),
    ("MEMORIA DE ACTUACIÓN\nProyecto: Alfa\nObjetivos: Detallar el alcance...", "memoria_actuacion"),
    ("Este es un documento de prueba para el tipo 4 con type_4_keyword.", None), # Change to "document_type_4" if rule added
    # Add test cases for the other 9 document types once their keywords/rules are defined
    # ("Texto para el documento tipo 5...", "document_type_5"),
    # ...
    # ("Texto para el documento tipo 12...", "document_type_12"),
    ("Un texto genérico sin palabras clave específicas.", None),
    ("", None), # Empty text
    ("Este es un certificado final de obra pero sin la firma del director de obra.", None), # Partial match for certificado_final
    ("Solo la palabra factura no es suficiente.", None), # Partial match for factura
]

@pytest.mark.parametrize("text_input, expected_type", test_data)
def test_document_classification(text_input: str, expected_type: Optional[str]):
    """
    Tests the DocumentClassifier with various inputs.
    """
    classifier = DocumentClassifier(text_input)
    assert classifier.classify() == expected_type

def test_classifier_with_real_examples_if_available():
    """
    Placeholder for tests using more realistic (and potentially longer) text snippets
    from actual documents, if they become available.
    """
    # Example for Certificado Final
    cf_text = """
    CERTIFICADO FINAL DE OBRA
    Obra: Vivienda Unifamiliar en Calle Falsa 123
    Promotor: D. Ejemplo Promotor
    Constructor: Construcciones ABC S.L.
    Director de Obra: D. Arquitecto Uno (Colegiado Nº 111)
    Director de Ejecución de la Obra: D. Aparejador Dos (Colegiado Nº 222)
    Fecha: A Coruña, 15 de mayo de 2023
    Observaciones: Ninguna.
    """
    classifier_cf = DocumentClassifier(cf_text)
    # The mock rule needs "director de obra", which is present.
    assert classifier_cf.classify() == "certificado_final"

    # Example for Factura
    factura_text = """
    FACTURAS Paco S.L.
    C/ Principal, 1
    28001 Madrid

    Factura Nº: F2023/001
    Fecha: 20/11/2023

    Cliente:
    Empresa Cliente S.A.
    C/ Secundaria, 2
    08001 Barcelona

    Concepto                                     Precio    IVA   Total
    Servicio de consultoría                      1000.00   21%   1210.00

    Total: 1210.00 EUR
    """
    classifier_factura = DocumentClassifier(factura_text)
    # The mock rule needs "factura nº" and "total:", both are present.
    assert classifier_factura.classify() == "factura"

    # Example for Memoria de Actuación (adjust keywords in mock if needed)
    memoria_text = """
    MEMORIA DE ACTUACIÓN TÉCNICA
    Proyecto: Instalación Solar Fotovoltaica
    Emplazamiento: Parcela XYZ, Término Municipal de Solville
    Promotor: EcoEnergías S.A.

    1. Objeto de la actuación
    ...
    2. Objetivos:
       - Reducir la dependencia energética.
       - Cumplir con normativa de eficiencia.
    ...
    """
    classifier_memoria = DocumentClassifier(memoria_text)
    # Mock rule "memoria de actuación" and "objetivos:"
    assert classifier_memoria.classify() == "memoria_actuacion"


if __name__ == '__main__':
    # This allows running pytest directly on this file if needed
    # (though typically pytest is run from the project root)
    pytest.main([__file__])
