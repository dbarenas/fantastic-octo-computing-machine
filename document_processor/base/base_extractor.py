from abc import ABC, abstractmethod
from aws_lib.textract import extract_text_from_document

class BaseExtractor(ABC):
    def __init__(self, bucket_name: str, document_key: str):
        self.bucket_name = bucket_name
        self.document_key = document_key
        self.text = self._load_text_from_s3()

    def _load_text_from_s3(self) -> str:
        """
        Loads text from an S3 document using AWS Textract.
        """
        # Assuming region_name is configured elsewhere or using a default
        # For now, let's hardcode it or consider making it configurable
        region_name = "us-east-1" # Or get from a config file/environment variable
        return extract_text_from_document(self.bucket_name, self.document_key, region_name)

    @abstractmethod
    def extract(self) -> dict:
        """
        Extracts relevant information from the document text.
        Should be implemented by subclasses for specific document types.
        """
        pass
