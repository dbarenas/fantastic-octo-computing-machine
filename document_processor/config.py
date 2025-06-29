# Parámetros generales del sistema

# Example:
# AWS_REGION = "us-east-1"
# TEXTRACT_S3_BUCKET = "your-textract-s3-bucket"
# DATABASE_URL = "sqlite:///./documents.db" # Example for SQLAlchemy

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Supported document types (example)
# SUPPORTED_DOCUMENT_TYPES = [
# "certificado_final",
# "factura",
# "memoria_actuacion",
#     # ... other 9 types
# ]

# Parameters for validation rules (can be loaded from here or a DB)
# e.g., MAX_VALID_DATE_CERTIFICADO_FINAL = "2026-06-30"

print("Configuration loaded.")
