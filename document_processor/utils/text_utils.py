# Utility functions for text processing and cleaning

import re
import unicodedata

def normalize_text(text: str) -> str:
    """
    Normalizes text by:
    - Converting to lowercase.
    - Removing extra whitespace (leading/trailing, multiple spaces to single).
    - Normalizing Unicode characters (e.g., accented characters to their base form if desired,
      or ensuring consistent Unicode representation). For now, simple NFC normalization.
    """
    if not text:
        return ""
    text = text.lower()
    text = unicodedata.normalize('NFC', text) # Normalize Unicode characters
    text = re.sub(r'\s+', ' ', text).strip() # Replace multiple whitespace with single, and strip
    return text

def remove_special_characters(text: str, keep_chars: str = " .,;:-_()/&%@") -> str:
    """
    Removes special characters from text, keeping alphanumeric and specified characters.
    :param text: The input string.
    :param keep_chars: A string of characters to keep in addition to alphanumeric.
    """
    if not text:
        return ""
    # Create a regex pattern to keep alphanumeric and the specified characters
    # The pattern [^a-zA-Z0-9\s...] matches any character NOT in the set.
    # We need to escape regex special characters within keep_chars if any (e.g., ., -, [, ])
    escaped_keep_chars = re.escape(keep_chars)
    pattern = f"[^a-zA-Z0-9{escaped_keep_chars}]"
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def extract_emails(text: str) -> list[str]:
    """
    Extracts all email addresses from a given text.
    """
    if not text:
        return []
    # A common regex for matching email addresses
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_regex, text)

def extract_numbers(text: str, convert_to_float: bool = False) -> list:
    """
    Extracts all sequences of digits (integers or decimals) from text.
    Can optionally convert them to float.
    """
    if not text:
        return []
    # Regex to find numbers, including decimals.
    # It also handles numbers with commas as thousands separators (which are removed).
    text_no_commas = text.replace(',', '') # Remove thousands separators for simplicity
    number_regex = r'\b\d+\.?\d*\b' # Matches integers and decimals

    found_strings = re.findall(number_regex, text_no_commas)
    if convert_to_float:
        numbers = []
        for s in found_strings:
            try:
                numbers.append(float(s))
            except ValueError:
                pass # Should not happen with this regex if input is clean
        return numbers
    return found_strings


if __name__ == '__main__':
    sample_text_1 = "  Esto es una PRUEBA   con    espacios extra y ácentos.  "
    normalized = normalize_text(sample_text_1)
    print(f"Original: '{sample_text_1}'")
    print(f"Normalized: '{normalized}'")

    sample_text_2 = "Texto con símbolos: !@#$%^&*()_+=-`~[]{}|;':\",./<>? y números 123."
    cleaned_spec_chars = remove_special_characters(sample_text_2)
    print(f"\nOriginal for special chars: '{sample_text_2}'")
    print(f"Cleaned (default keep): '{cleaned_spec_chars}'")
    cleaned_spec_chars_custom = remove_special_characters(sample_text_2, keep_chars=" .!?-")
    print(f"Cleaned (custom keep ' .!?-'): '{cleaned_spec_chars_custom}'")

    email_text = "Contact us at support@example.com or sales.team@company.co.uk for more info."
    emails = extract_emails(email_text)
    print(f"\nText with emails: '{email_text}'")
    print(f"Extracted emails: {emails}")

    empty_email_text = "No emails here."
    no_emails = extract_emails(empty_email_text)
    print(f"Text with no emails: '{empty_email_text}'")
    print(f"Extracted emails: {no_emails}")

    number_text = "El precio es 1.234,56 EUR y la cantidad es 500. Otro valor: 78.90."
    str_numbers = extract_numbers(number_text)
    float_numbers = extract_numbers(number_text, convert_to_float=True)
    print(f"\nText with numbers: '{number_text}'")
    print(f"Extracted numbers (strings): {str_numbers}")
    print(f"Extracted numbers (floats): {float_numbers}")

    number_text_simple = "Values: 10 20.5 300"
    str_numbers_simple = extract_numbers(number_text_simple)
    float_numbers_simple = extract_numbers(number_text_simple, convert_to_float=True)
    print(f"\nText with numbers: '{number_text_simple}'")
    print(f"Extracted numbers (strings): {str_numbers_simple}")
    print(f"Extracted numbers (floats): {float_numbers_simple}")
