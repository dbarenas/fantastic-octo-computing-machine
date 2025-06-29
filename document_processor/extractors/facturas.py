from base.base_extractor import BaseExtractor
import re

class FacturaExtractor(BaseExtractor):
    def extract(self) -> dict:
        """
        Extracts information specific to invoices (facturas).
        This is a placeholder and needs to be implemented with actual
        extraction logic for invoices.
        """
        # Example fields for an invoice:
        # - Numero de factura (Invoice number)
        # - Fecha de emision (Issue date)
        # - Fecha de vencimiento (Due date)
        # - Datos del emisor (Sender details: Nombre, NIF/CIF, Direccion)
        # - Datos del receptor (Receiver details: Nombre, NIF/CIF, Direccion)
        # - Lineas de factura (Invoice lines: Descripcion, Cantidad, Precio Unitario, Total Linea)
        # - Base imponible (Taxable base)
        # - IVA (VAT amount and percentage)
        # - Total factura (Total amount)

        # Placeholder logic:
        return {
            "numero_factura": self._extraer_numero_factura(),
            "fecha_emision": self._extraer_fecha_emision(),
            "total_factura": self._extraer_total(),
            "emisor_nombre": "Placeholder Emisor S.L.", # Placeholder
            "receptor_nombre": "Placeholder Cliente S.A." # Placeholder
        }

    def _extraer_numero_factura(self):
        # Example: search for "Factura Nº XXXXX" or "Invoice # XXXXX"
        match = re.search(r"(?:Factura N[ºo\.]?|Invoice #)\s*([A-Za-z0-9\-]+)", self.text, re.IGNORECASE)
        return match.group(1) if match else None

    def _extraer_fecha_emision(self):
        # Example: search for common date patterns near "Fecha Factura" or "Date"
        # This is highly dependent on document layout.
        match = re.search(r"(?:Fecha Factura|Date)[:\s]*(\d{2}[-/]\d{2}[-/]\d{4})", self.text, re.IGNORECASE)
        if match:
            return match.group(1)
        # Try another common format or keyword
        match = re.search(r"(\d{2}/\d{2}/\d{4})", self.text) # A generic date, might not be the invoice date
        return match.group(1) if match else None


    def _extraer_total(self):
        # Example: search for "Total EUR", "Total:", "Amount Due" followed by a number
        # This requires careful regex to capture currency symbols and decimal points
        match = re.search(r"(?:TOTAL|Total Factura|Importe Total|Amount Due)\s*[:€$]?\s*([\d\.,]+)", self.text, re.IGNORECASE)
        if match:
            # Clean up the extracted number (remove currency, convert comma to dot for float)
            total_str = match.group(1).replace('€', '').replace('$', '').replace('.', '').replace(',', '.')
            try:
                return float(total_str)
            except ValueError:
                return None
        return None

if __name__ == '__main__':
    sample_invoice_text = """
    FACTURA Nº F2023-001
    Fecha Factura: 25/12/2023

    Emisor: Proveedor Ejemplo S.L.
    Cliente: Comprador Test S.A.

    Concepto         Cantidad    Precio      Total
    Servicio X       1           100.00      100.00
    Servicio Y       2           50.00       100.00

    Base Imponible: 200.00
    IVA (21%): 42.00
    Total Factura: 242.00 EUR
    """
    extractor = FacturaExtractor(sample_invoice_text)
    data = extractor.extract()
    print("Extracted Invoice Data (Placeholder):")
    for key, value in data.items():
        print(f"- {key}: {value}")

    sample_invoice_text_2 = """
    Invoice # INV-789
    Date: 01/01/2024
    Amount Due $ 150.55
    """
    extractor_2 = FacturaExtractor(sample_invoice_text_2)
    data_2 = extractor_2.extract()
    print("\nExtracted Invoice Data 2 (Placeholder):")
    for key, value in data_2.items():
        print(f"- {key}: {value}")
