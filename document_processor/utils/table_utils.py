# Utility functions for table extraction and processing (if documents contain tables)

# Table extraction can be very complex and might involve:
# - Using OCR capabilities that specifically identify tables (like Textract's AnalyzeDocument with 'TABLES' feature).
# - PDF parsing libraries that can interpret table structures (e.g., camelot-py, tabula-py).
# - Computer vision models if dealing with image-based tables.

# This file will provide placeholders for such functionalities.

# from typing import List, Dict, Any, Optional
# import pandas as pd # Pandas DataFrames are a common way to represent tables

class TableExtractor:
    def __init__(self, ocr_results: Optional[Any] = None, pdf_path: Optional[str] = None):
        """
        Initializes the table extractor.
        :param ocr_results: Raw results from an OCR service (e.g., Textract response)
                           that might contain table information.
        :param pdf_path: Path to a PDF file, if using PDF-specific table extraction libraries.
        """
        self.ocr_results = ocr_results
        self.pdf_path = pdf_path
        print("TableExtractor initialized (mock).")

    def extract_tables_from_textract_response(self, textract_response: dict) -> List[pd.DataFrame]:
        """
        Parses a Textract 'AnalyzeDocument' response (with 'TABLES' feature)
        and converts detected tables into a list of pandas DataFrames.

        This is a simplified placeholder. A real implementation needs to handle:
        - Merged cells.
        - Relationships between TABLE, CELL, and WORD blocks.
        - Confidence scores.
        """
        # tables_data = []
        # if not textract_response or "Blocks" not in textract_response:
        #     return tables_data

        # table_blocks = [block for block in textract_response["Blocks"] if block["BlockType"] == "TABLE"]
        # cell_blocks_by_id = {block["Id"]: block for block in textract_response["Blocks"] if block["BlockType"] == "CELL"}
        # word_blocks_by_id = {block["Id"]: block for block in textract_response["Blocks"] if block["BlockType"] == "WORD"}

        # for table_block in table_blocks:
        #     # Determine table dimensions (rows, columns) - Textract provides this
        #     # Iterate through cell relationships in the table block
        #     # For each cell, get its text content by looking up child WORD blocks
        #     # Assemble into a 2D list or directly into a DataFrame

        #     # Placeholder:
        #     num_rows = table_block.get("Rows", 0) # This is not directly in Textract, needs calculation
        #     num_cols = table_block.get("Columns", 0) # Same as above

        #     # This is a very naive representation. A real parser is complex.
        #     # For instance, you'd iterate `table_block['Relationships']` of type `CHILD` to find `CELL` IDs,
        #     # then for each `CELL`, find its `WORD` children to get text.
        #     # Then map `RowIndex`, `ColumnIndex` from `CELL` block to DataFrame positions.

        #     if num_rows > 0 and num_cols > 0: # A very rough guess for placeholder
        #         data = [["(mock cell)" for _ in range(num_cols)] for _ in range(num_rows)]
        #         df = pd.DataFrame(data, columns=[f"Col{i+1}" for i in range(num_cols)])
        #         tables_data.append(df)
        #     else: # Fallback mock if dimensions are hard to guess from placeholder
        #         df = pd.DataFrame({
        #             "Header1 (mock)": ["R1C1", "R2C1"],
        #             "Header2 (mock)": ["R1C2", "R2C2"]
        #         })
        #         tables_data.append(df)

        print(f"Simulating table extraction from Textract response. Found 1 mock table.")
        # Simulate finding one table
        mock_df = pd.DataFrame({
            "Column A (Simulated)": [1, 2, 3],
            "Column B (Simulated)": ["Data X", "Data Y", "Data Z"],
            "Column C (Simulated)": [10.5, 20.3, 30.1]
        })
        return [mock_df]

    def extract_tables_with_camelot(self) -> List[pd.DataFrame]:
        """
        Extracts tables from a PDF using camelot-py.
        Requires camelot-py and its dependencies (Ghostscript, Tkinter) to be installed.
        """
        # if not self.pdf_path:
        #     print("PDF path not provided for Camelot extraction.")
        #     return []
        # try:
        #     import camelot
        #     # 'stream' method is good for tables with clear lines, 'lattice' for tables with no lines.
        #     tables = camelot.read_pdf(self.pdf_path, pages='all', flavor='lattice')
        #     return [table.df for table in tables]
        # except ImportError:
        #     print("camelot-py library is not installed. Cannot extract tables with Camelot.")
        #     return []
        # except Exception as e:
        #     print(f"Error extracting tables with Camelot from {self.pdf_path}: {e}")
        #     return []
        if not self.pdf_path:
            print("PDF path not provided for Camelot simulation.")
            return []
        print(f"Simulating table extraction with Camelot for PDF: {self.pdf_path}. Found 1 mock table.")
        mock_df = pd.DataFrame({
            "Camelot Header 1": ["Val1", "Val2"],
            "Camelot Header 2": ["Val3", "Val4"]
        })
        return [mock_df]

def dataframe_to_json_serializable(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Converts a pandas DataFrame into a JSON-serializable list of dictionaries (one per row).
    Handles potential NaNs or other non-serializable types if necessary.
    """
    # return df.to_dict(orient='records')
    # More robustly, handle NaNs which are not valid JSON `null` directly via to_json then parse
    # For simplicity now, to_dict is often fine if data is clean or further processed.
    # Replace NaN with None for JSON compatibility
    return df.where(pd.notnull(df), None).to_dict(orient='records')


if __name__ == '__main__':
    print("--- Mock Textract Table Extraction ---")
    # Simulate a Textract response structure (very simplified)
    mock_textract_response = {
        "Blocks": [
            {"BlockType": "TABLE", "Id": "table1", "Rows": 2, "Columns": 2}, # Simplified attributes
            # ... other blocks like CELL, WORD would be here in a real response
        ]
    }
    extractor_textract = TableExtractor(ocr_results=mock_textract_response)
    textract_tables = extractor_textract.extract_tables_from_textract_response(mock_textract_response)
    if textract_tables:
        print(f"Found {len(textract_tables)} table(s) from Textract (mock):")
        for i, table_df in enumerate(textract_tables):
            print(f"Table {i+1}:\n{table_df}\n")
            serializable_table = dataframe_to_json_serializable(table_df)
            print(f"Serializable version of Table {i+1}:\n{serializable_table}\n")
    else:
        print("No tables extracted from Textract (mock).")

    print("\n--- Mock Camelot Table Extraction ---")
    # Create a dummy PDF file name for the simulation
    dummy_pdf_file = "dummy_document_for_camelot.pdf"
    extractor_camelot = TableExtractor(pdf_path=dummy_pdf_file)
    camelot_tables = extractor_camelot.extract_tables_with_camelot()
    if camelot_tables:
        print(f"Found {len(camelot_tables)} table(s) with Camelot (mock):")
        for i, table_df in enumerate(camelot_tables):
            print(f"Table {i+1}:\n{table_df}\n")
    else:
        print("No tables extracted with Camelot (mock).")

    # Example of dataframe_to_json_serializable with NaN
    df_with_nan = pd.DataFrame({
        'col1': [1, 2, np.nan],
        'col2': ['a', np.nan, 'c']
    })
    import numpy as np # for pd.NA or np.nan
    print(f"\n--- Testing dataframe_to_json_serializable with NaN ---")
    print(f"Original DataFrame with NaN:\n{df_with_nan}")
    json_serializable_nan = dataframe_to_json_serializable(df_with_nan.copy()) # Use copy
    print(f"JSON Serializable (NaN replaced with None):\n{json_serializable_nan}")
