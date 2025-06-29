# Utility functions for file operations

import os
import shutil
from typing import Optional, List

def get_file_extension(file_path: str) -> Optional[str]:
    """
    Returns the file extension from a file path (e.g., '.pdf', '.txt').
    Returns None if no extension is found.
    """
    if not file_path or not isinstance(file_path, str):
        return None
    _, ext = os.path.splitext(file_path)
    return ext.lower() if ext else None

def get_file_name(file_path: str, include_extension: bool = True) -> Optional[str]:
    """
    Returns the file name from a file path.
    :param file_path: The full path to the file.
    :param include_extension: If True, includes the extension in the returned name.
    """
    if not file_path or not isinstance(file_path, str):
        return None
    base_name = os.path.basename(file_path)
    if not include_extension:
        return os.path.splitext(base_name)[0]
    return base_name

def create_directory_if_not_exists(dir_path: str):
    """
    Creates a directory if it does not already exist.
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True) # exist_ok=True handles race conditions
            print(f"Directory created: {dir_path}")
        except OSError as e:
            print(f"Error creating directory {dir_path}: {e}")
            raise # Re-raise the exception if creation fails critically
    # else:
    #     print(f"Directory already exists: {dir_path}")


def save_uploaded_file(upload_file, destination_path: str) -> bool:
    """
    Saves an uploaded file (e.g., from FastAPI's UploadFile) to a destination.
    Assumes `upload_file` has a `file` attribute (like BytesIO) and a `filename`.
    """
    create_directory_if_not_exists(os.path.dirname(destination_path))
    try:
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        print(f"File '{getattr(upload_file, 'filename', 'unknown')}' saved to '{destination_path}'")
        return True
    except Exception as e:
        print(f"Error saving uploaded file to {destination_path}: {e}")
        return False
    finally:
        if hasattr(upload_file, 'close'): # Some file-like objects might need closing
             upload_file.close()


def read_file_bytes(file_path: str) -> Optional[bytes]:
    """
    Reads a file and returns its content as bytes.
    Returns None if the file cannot be read.
    """
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def list_files_in_directory(dir_path: str, extension_filter: Optional[str] = None) -> List[str]:
    """
    Lists all files in a given directory, optionally filtering by extension.
    Returns a list of full file paths.
    :param dir_path: The directory to scan.
    :param extension_filter: Optional file extension (e.g., '.pdf', 'txt') to filter by.
                           If provided, include the dot.
    """
    if not os.path.isdir(dir_path):
        print(f"Directory not found: {dir_path}")
        return []

    files_found = []
    for item_name in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item_name)
        if os.path.isfile(item_path):
            if extension_filter:
                if item_name.lower().endswith(extension_filter.lower()):
                    files_found.append(item_path)
            else:
                files_found.append(item_path)
    return files_found


if __name__ == '__main__':
    test_file_path = "/path/to/some/document.PDF"
    print(f"--- Testing with path: {test_file_path} ---")
    print(f"Extension: {get_file_extension(test_file_path)}")
    print(f"File name (with ext): {get_file_name(test_file_path)}")
    print(f"File name (no ext): {get_file_name(test_file_path, include_extension=False)}")

    test_file_no_ext = "/path/to/some/document"
    print(f"\n--- Testing with path: {test_file_no_ext} ---")
    print(f"Extension: {get_file_extension(test_file_no_ext)}")
    print(f"File name (with ext): {get_file_name(test_file_no_ext)}")

    # Directory operations (be careful with actual file system changes)
    # For testing, these would ideally use a temporary directory.
    # import tempfile
    # temp_dir = tempfile.mkdtemp()
    # print(f"\n--- Testing directory operations in: {temp_dir} ---")

    # try:
    #     my_test_dir = os.path.join(temp_dir, "my_test_subdir")
    #     create_directory_if_not_exists(my_test_dir)
    #     create_directory_if_not_exists(my_test_dir) # Try creating again (should not fail)

    #     # Create some dummy files for listing
    #     with open(os.path.join(my_test_dir, "file1.txt"), "w") as f: f.write("text")
    #     with open(os.path.join(my_test_dir, "file2.pdf"), "w") as f: f.write("pdf")
    #     with open(os.path.join(my_test_dir, "file3.TXT"), "w") as f: f.write("text upper")

    #     all_files = list_files_in_directory(my_test_dir)
    #     print(f"All files in {my_test_dir}: {all_files}")

    #     txt_files = list_files_in_directory(my_test_dir, extension_filter=".txt")
    #     print(f".txt files in {my_test_dir}: {txt_files}")

    #     pdf_files = list_files_in_directory(my_test_dir, extension_filter=".pdf")
    #     print(f".pdf files in {my_test_dir}: {pdf_files}")

    #     # Test read_file_bytes
    #     file1_path = os.path.join(my_test_dir, "file1.txt")
    #     file1_bytes = read_file_bytes(file1_path)
    #     if file1_bytes:
    #         print(f"Bytes of {file1_path}: {file1_bytes} (Decoded: {file1_bytes.decode()})")
    #     non_existent_bytes = read_file_bytes(os.path.join(my_test_dir, "nonexistent.dat"))
    #     if non_existent_bytes is None:
    #         print("Correctly handled non-existent file for read_file_bytes.")

    # finally:
    #     # Clean up the temporary directory
    #     # shutil.rmtree(temp_dir)
    #     # print(f"Cleaned up temporary directory: {temp_dir}")
    #     pass # In a real test, ensure cleanup. For placeholder, skip actual FS ops.
    print("\n(Skipping file system operations in __main__ for placeholder utils)")
