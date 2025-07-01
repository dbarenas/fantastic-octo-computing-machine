import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from src.document_processing.core.base import OCRExtractor, Document
from typing import Optional
import os

class TextractOCRExtractor(OCRExtractor):
    """
    OCR extractor implementation using AWS Textract.

    This extractor assumes that AWS credentials and region are configured
    in the environment where the code runs, typically via:
    - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
    - Shared credential file (~/.aws/credentials)
    - IAM roles for EC2 instances, ECS tasks, or Lambda functions.
    """
    def __init__(self, region_name: Optional[str] = None, s3_bucket_for_large_docs: Optional[str] = None):
        """
        Initializes the TextractOCRExtractor.

        Args:
            region_name (Optional[str]): The AWS region to use. If None, boto3 will attempt
                                         to determine it from the environment/configuration.
            s3_bucket_for_large_docs (Optional[str]): S3 bucket name to use for temporarily
                                                      uploading large documents for asynchronous Textract processing.
                                                      (Asynchronous processing is not implemented in this initial version).
        """
        try:
            if region_name:
                self.textract_client = boto3.client('textract', region_name=region_name)
            else:
                self.textract_client = boto3.client('textract') # Relies on default config
            self.s3_bucket_for_large_docs = s3_bucket_for_large_docs
            # Test client connection (optional, can raise error early if config is wrong)
            # self.textract_client.list_detectors() # Example call, not a real Textract API, find a suitable one
            print(f"TextractOCRExtractor initialized. AWS Region: {self.textract_client.meta.region_name}")
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"Error: AWS credentials not found or incomplete. Please configure AWS credentials. {e}")
            raise  # Re-raise to prevent use of a non-functional extractor
        except ClientError as e:
            print(f"Error initializing Textract client: {e}")
            raise
        except Exception as e: # Catch other potential boto3/config issues
            print(f"An unexpected error occurred during TextractOCRExtractor initialization: {e}")
            raise


    def _read_document_bytes(self, document_path: str) -> bytes:
        """Reads document content as bytes."""
        try:
            with open(document_path, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: Document file not found at {document_path}")
            raise
        except Exception as e:
            print(f"Error reading document file {document_path}: {e}")
            raise

    def extract_text(self, document: Document) -> str:
        """
        Extracts text from a document using AWS Textract's `detect_document_text` (synchronous).

        Args:
            document (Document): The document object with `document_path`.

        Returns:
            str: The extracted text, or an empty string if extraction fails.
        """
        print(f"TextractOCRExtractor: Starting OCR for document {document.document_id} at {document.document_path}...")

        if not os.path.exists(document.document_path):
            error_msg = f"Document file not found: {document.document_path}"
            print(f"TextractOCRExtractor: {error_msg}")
            document.validation_errors.append(error_msg) # Or a more specific error list
            return ""

        try:
            document_bytes = self._read_document_bytes(document.document_path)

            # For simplicity, this example uses detect_document_text (synchronous).
            # For production, consider document size limits and asynchronous operations
            # (start_document_text_detection, get_document_text_detection) for larger files,
            # which would typically involve S3.
            # Max file size for sync operations: PDF: 5MB, Image: 5MB. Pages: PDF: 1, Image: 1.
            # If your document type is PDF and has multiple pages, or is larger, you'll need async.
            # This basic version assumes single-page images or PDFs fitting sync limits.

            response = self.textract_client.detect_document_text(
                Document={'Bytes': document_bytes}
            )

            extracted_lines = []
            for item in response.get("Blocks", []):
                if item.get("BlockType") == "LINE":
                    extracted_lines.append(item.get("Text", ""))

            full_text = "\n".join(extracted_lines)
            document.raw_text = full_text # Update the document object
            print(f"TextractOCRExtractor: OCR complete for {document.document_id}. {len(extracted_lines)} lines extracted.")
            return full_text

        except (NoCredentialsError, PartialCredentialsError):
            error_msg = "AWS credentials not found or incomplete. Cannot call Textract."
            print(f"TextractOCRExtractor: {error_msg}")
            document.validation_errors.append(error_msg)
            return ""
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            error_message = e.response.get('Error', {}).get('Message')
            error_msg = f"AWS Textract API error: {error_code} - {error_message}. Document: {document.document_id}"
            print(f"TextractOCRExtractor: {error_msg}")
            document.validation_errors.append(error_msg)
            # You might want to inspect specific error codes, e.g., for unsupported document types, large files, etc.
            # For example, TextractUnsupportedDocumentException, DocumentTooLargeException
            return ""
        except FileNotFoundError: # Already handled by os.path.exists, but good for _read_document_bytes
            error_msg = f"File not found during Textract processing: {document.document_path}"
            print(f"TextractOCRExtractor: {error_msg}")
            document.validation_errors.append(error_msg)
            return ""
        except Exception as e:
            error_msg = f"An unexpected error occurred during Textract OCR for {document.document_id}: {e}"
            print(f"TextractOCRExtractor: {error_msg}")
            document.validation_errors.append(error_msg)
            return ""

# Example of how one might extend for asynchronous operations (Not fully implemented here)
# class TextractAsyncOCRExtractor(TextractOCRExtractor):
#     def extract_text_async(self, document: Document, s3_object_key: str) -> str:
#         if not self.s3_bucket_for_large_docs:
#             raise ValueError("S3 bucket for large documents not configured for async Textract.")
#         # 1. Upload to S3 (if not already there)
#         # self.s3_client.upload_file(document.document_path, self.s3_bucket_for_large_docs, s3_object_key)
#         # 2. Start Textract job
#         # response = self.textract_client.start_document_text_detection(
#         #     DocumentLocation={'S3Object': {'Bucket': self.s3_bucket_for_large_docs, 'Name': s3_object_key}}
#         # )
#         # job_id = response['JobId']
#         # 3. Poll for completion (or use SNS notifications)
#         # ... get results using get_document_text_detection
#         pass
