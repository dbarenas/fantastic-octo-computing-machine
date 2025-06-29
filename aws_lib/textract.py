from textractor import Textractor
from textractor.data.constants import TextractFeatures

def extract_text_from_document(bucket_name: str, document_key: str, region_name: str = "us-east-1"):
    """
    Extracts text from a document stored in S3 using Amazon Textract.

    :param bucket_name: The name of the S3 bucket where the document is stored.
    :param document_key: The key of the document in the S3 bucket.
    :param region_name: The AWS region where Textract service is available.
    :return: Extracted text as a string.
    """
    extractor = Textractor(region_name=region_name)
    # Note: The Textractor library uses the default AWS session configured for boto3.
    # It will automatically use the credentials and region from the environment
    # or AWS configuration files if not explicitly passed to its constructor.

    response = extractor.start_document_text_detection(
        file_source=f"s3://{bucket_name}/{document_key}",
        s3_upload_path=f"s3://{bucket_name}/textract-output/", # Optional: specify an output path for Textract results
        save_image=False
    )

    return response.text
