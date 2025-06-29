# Conexión a base de datos y gestión de sesiones (si se usa ORM como SQLAlchemy)

# import sqlalchemy
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from config import DATABASE_URL #DATABASE_URL = "sqlite:///./documents.db"

# For a simple setup without a full ORM immediately, this file might just
# define connection parameters or helper functions for a direct DB driver (e.g., psycopg2, sqlite3).

# --- SQLAlchemy Example (if chosen) ---
# SQLALCHEMY_DATABASE_URL = DATABASE_URL # From config.py

# # The engine is the core interface to the database
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     connect_args={"check_same_thread": False} # Needed for SQLite only
# )

# # SessionLocal class is a factory for new Session objects
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class for declarative class definitions (ORM models)
# Base = declarative_base()

# def get_db_session():
#     """
#     Dependency to get a DB session.
#     Ensures the session is closed after the request.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def create_tables():
#     """
#     Creates all tables in the database defined by Base's subclasses.
#     Call this once at application startup if tables don't exist.
#     """
#     # Import all models here before calling create_all!
#     # from .models import DocumentModel # Example import
#     Base.metadata.create_all(bind=engine)
#     print("Database tables (potentially) created based on ORM models.")

# --- End SQLAlchemy Example ---


# --- Simpler SQLite3 example (without ORM for now) ---
import sqlite3
# from config import DATABASE_URL # Assume DATABASE_URL = "documents.db" for this example
DATABASE_FILE = "documents.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def initialize_database():
    """
    Initializes the database by creating necessary tables if they don't exist.
    This is a simplified version. `db/models.py` would define the schema more robustly,
    especially if using an ORM.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for storing document metadata and processing status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        file_name TEXT NOT NULL,
        file_type TEXT,
        upload_timestamp TEXT NOT NULL,
        processing_status TEXT NOT NULL, -- (pending, ocr, classified, extracted, validated, error)
        document_type_classified TEXT, -- Classified type (e.g., factura, certificado_final)
        raw_text_path TEXT, -- Path to stored raw text (if too large for DB field)
        error_message TEXT,
        last_updated_timestamp TEXT
    )
    """)

    # Table for storing extracted fields (generic JSON store or EAV pattern)
    # For simplicity, using JSON store here.
    # For more complex querying on specific fields, an EAV model or separate tables per doc type might be better.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extracted_data (
        document_id TEXT PRIMARY KEY,
        data_json TEXT, -- Store extracted fields as a JSON string
        FOREIGN KEY (document_id) REFERENCES documents (id)
    )
    """)

    # Table for storing validation results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS validation_results (
        document_id TEXT PRIMARY KEY,
        is_overall_valid INTEGER, -- Boolean (0 or 1)
        results_json TEXT, -- Store detailed validation checks as JSON
        FOREIGN KEY (document_id) REFERENCES documents (id)
    )
    """)

    # Potentially a table for RAG system to link document segments to embeddings or for quick lookup
    # cursor.execute("""
    # CREATE TABLE IF NOT EXISTS rag_document_segments (
    #     segment_id TEXT PRIMARY KEY,
    #     document_id TEXT NOT NULL,
    #     segment_text TEXT,
    #     embedding_vector BLOB, -- Or path to where embedding is stored
    #     FOREIGN KEY (document_id) REFERENCES documents (id)
    # )
    # """)

    conn.commit()
    conn.close()
    print(f"Database '{DATABASE_FILE}' initialized/checked.")

if __name__ == '__main__':
    print("Initializing database (if run directly)...")
    initialize_database()

    # Example of connecting (SQLAlchemy way)
    # print(f"SQLAlchemy Engine configured for: {SQLALCHEMY_DATABASE_URL if 'SQLALCHEMY_DATABASE_URL' in locals() else 'Not configured'}")
    # if 'create_tables' in locals():
    #     # create_tables() # Be careful running this directly if you have data
    #     pass

    # Example of connecting (simple sqlite3 way)
    # try:
    #     conn = get_db_connection()
    #     print(f"Successfully connected to SQLite database: {DATABASE_FILE}")
    #     conn.close()
    # except Exception as e:
    #     print(f"Error connecting to SQLite database: {e}")
