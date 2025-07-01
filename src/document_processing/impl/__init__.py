# This file makes 'impl' a Python subpackage.

from .documents import PDFDocument
from .extractors import TesseractOCRExtractor #, AzureDocumentIntelligenceExtractor (if it was kept)
from .aws_extractors import TextractOCRExtractor
from .classifiers import InvoiceClassifier, GeneralDocumentClassifier #, MLDocumentClassifier (if kept)
from .retrievers import InvoiceFieldRetriever, GeneralFieldRetriever #, NERFieldRetriever (if kept)
from .validators import DataLengthValidator, RegexValidator
from .processes import FinancialProcess

__all__ = [
    "PDFDocument", # Add ImageDocument if it's meant to be public
    "TesseractOCRExtractor",
    # "AzureDocumentIntelligenceExtractor", # If kept and public
    "TextractOCRExtractor",
    "InvoiceClassifier",
    "GeneralDocumentClassifier",
    # "MLDocumentClassifier", # If kept and public
    "InvoiceFieldRetriever",
    "GeneralFieldRetriever",
    # "NERFieldRetriever", # If kept and public
    "DataLengthValidator",
    "RegexValidator", # Add DateFormatValidator, AllowedValuesValidator if public
    "FinancialProcess",
]
# Let's clean up __all__ to reflect current concrete classes more accurately.
# Assuming ImageDocument, other validators etc. are also for general use.

# Re-generating __all__ based on the imports that are not commented out:
__all__ = [
    "PDFDocument",
    "ImageDocument", # Added from documents.py as it was not commented out
    "TesseractOCRExtractor",
    "TextractOCRExtractor",
    "InvoiceClassifier",
    "GeneralDocumentClassifier",
    "InvoiceFieldRetriever",
    "GeneralFieldRetriever",
    "DataLengthValidator",
    "RegexValidator",
    "DateFormatValidator", # Added from validators.py
    "AllowedValuesValidator", # Added from validators.py
    "FinancialProcess",
]
