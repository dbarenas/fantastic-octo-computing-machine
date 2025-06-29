import boto3

def get_s3_client():
    """
    Initializes and returns a boto3 S3 client.

    Assumes AWS credentials and region are configured in the environment
    (e.g., through environment variables, shared credential file, or IAM roles).
    """
    return boto3.client("s3")
