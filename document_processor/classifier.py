# Clasificador de tipo de documento

# This module will be responsible for determining the type of a document
# based on its content (e.g., extracted text).

# Possible strategies:
# 1. Keyword-based classification.
# 2. Machine learning models (e.g., text classification).
# 3. Rule-based systems.

# For now, a simple placeholder.

# from config import SUPPORTED_DOCUMENT_TYPES # Assuming this will be defined

class DocumentClassifier:
    def __init__(self, text: str):
        self.text = text.lower() # Convert to lowercase for easier matching

    def classify(self) -> Optional[str]:
        """
        Classifies the document based on its text content.
        Returns the document type as a string (e.g., "certificado_final", "factura")
        or None if the type cannot be determined.
        """
        # This is a very basic example. A real implementation would be more robust.
        if "certificado final de obra" in self.text:
            return "certificado_final"
        elif "factura" in self.text and "cliente" in self.text and "total" in self.text:
            return "factura"
        elif "memoria de actuación" in self.text: # Example for another type
            return "memoria_actuacion"
        # ... add rules for other document types ...

        # Placeholder for the 12 types, assuming some keywords
        # This is highly dependent on the actual content of those 12 document types.
        # For a real system, these rules would need to be carefully defined or a ML model trained.
        # Example:
        # elif "document_type_3_keyword_1" in self.text and "document_type_3_keyword_2" in self.text:
        #     return "document_type_3"
        # ... up to document_type_12

        # if self.text contains keywords for type X: return "type_X"
        print(f"Attempting to classify document based on text snippet: '{self.text[:200]}...'")
        # In a real scenario, this would use more sophisticated logic or a trained model.
        # For now, it needs to be expanded with rules for all 12 document types.
        return None # Default if no type is matched

if __name__ == '__main__':
    example_text_cf = "Este es un Certificado Final de Obra..."
    classifier_cf = DocumentClassifier(example_text_cf)
    print(f"Classified as: {classifier_cf.classify()}")

    example_text_factura = "Factura No. 123\nCliente: Juan Perez\nTotal: $100"
    classifier_factura = DocumentClassifier(example_text_factura)
    print(f"Classified as: {classifier_factura.classify()}")

    example_text_unknown = "Texto de un documento no reconocido."
    classifier_unknown = DocumentClassifier(example_text_unknown)
    print(f"Classified as: {classifier_unknown.classify()}")
