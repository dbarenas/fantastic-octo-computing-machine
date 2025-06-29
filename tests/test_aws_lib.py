import unittest
from unittest.mock import patch, MagicMock
import boto3
from botocore.client import BaseClient

# Assuming aws_lib is in the parent directory or installed
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aws_lib.s3 import get_s3_client
from aws_lib.textract import extract_text_from_document
from textractor.data.text_linearization_config import TextLinearizationConfig

class TestAwsLib(unittest.TestCase):

    def test_get_s3_client(self):
        """
        Tests if get_s3_client returns a boto3 S3 client instance.
        """
        client = get_s3_client()
        self.assertIsNotNone(client)
        self.assertIsInstance(client, BaseClient)
        # Check if it's specifically an S3 client
        # Accessing a protected member _service_model is generally not recommended
        # but can be useful for such a check in tests.
        self.assertEqual(client._service_model.service_name, 's3')

    @patch('aws_lib.textract.Textractor')
    def test_extract_text_from_document(self, MockTextractor):
        """
        Tests the extract_text_from_document function with a mocked Textractor.
        """
        mock_bucket = "test-bucket"
        mock_key = "test-document.pdf"
        mock_region = "us-west-2"
        expected_text = "This is a test document."

        # Configure the mock Textractor instance
        mock_extractor_instance = MockTextractor.return_value

        # Mock the response object that start_document_text_detection would return
        mock_response = MagicMock()
        mock_response.text = expected_text
        # If you need to mock other attributes or methods of the response, do it here.
        # For example, if your actual code uses response.pages, mock response.pages as well.

        mock_extractor_instance.start_document_text_detection.return_value = mock_response

        # Call the function
        extracted_text = extract_text_from_document(mock_bucket, mock_key, region_name=mock_region)

        # Assertions
        MockTextractor.assert_called_once_with(region_name=mock_region)
        mock_extractor_instance.start_document_text_detection.assert_called_once_with(
            file_source=f"s3://{mock_bucket}/{mock_key}",
            s3_upload_path=f"s3://{mock_bucket}/textract-output/",
            save_image=False
        )
        self.assertEqual(extracted_text, expected_text)

if __name__ == '__main__':
    unittest.main()
