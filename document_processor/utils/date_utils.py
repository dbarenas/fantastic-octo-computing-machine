# Utility functions for date parsing, formatting, and validation

from datetime import datetime, date
from typing import Optional, List, Union
import re

# Common date formats to try when parsing
# Order matters: more specific formats should generally come before more generic ones.
COMMON_DATE_FORMATS = [
    "%d/%m/%Y",  # 01/12/2023
    "%d-%m-%Y",  # 01-12-2023
    "%Y-%m-%d",  # 2023-12-01
    "%Y/%m/%d",  # 2023/12/01
    "%d.%m.%Y",  # 01.12.2023
    "%m/%d/%Y",  # 12/01/2023 (US format, can be ambiguous)
    "%d %b %Y",  # 01 Dec 2023 (Requires locale or English month abbr)
    "%d %B %Y",  # 01 December 2023 (Requires locale or English month name)
    "%Y%m%d",    # 20231201 (No separator)
]

def parse_date_string(date_str: str, formats: Optional[List[str]] = None) -> Optional[date]:
    """
    Tries to parse a date string using a list of common formats.
    Returns a datetime.date object if successful, otherwise None.
    :param date_str: The date string to parse.
    :param formats: Optional list of format strings to try. Defaults to COMMON_DATE_FORMATS.
    """
    if not date_str or not isinstance(date_str, str):
        return None

    target_formats = formats or COMMON_DATE_FORMATS

    for fmt in target_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except (ValueError, TypeError):
            continue
    return None

def find_and_parse_dates(text: str, formats: Optional[List[str]] = None) -> List[date]:
    """
    Finds all substrings in a text that look like dates and attempts to parse them.
    This is a basic implementation and might need more sophisticated regex for complex cases.
    Returns a list of unique datetime.date objects found.
    """
    if not text:
        return []

    # Basic regex to find potential date-like strings.
    # This regex is quite broad and will capture many things that then need to be validated by strptime.
    # It looks for sequences like dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd, etc.
    # It also tries to capture d Mon YYYY and d Month YYYY.
    date_pattern = re.compile(
        r'\b('
        r'(?:\d{1,2}[./-]\d{1,2}[./-]\d{2,4})|'  # dd/mm/yy or dd/mm/yyyy and variations
        r'(?:\d{4}[./-]\d{1,2}[./-]\d{1,2})|'  # yyyy/mm/dd and variations
        r'(?:\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})|' # d Mon YYYY (case-insensitive for month)
        r'(?:\d{8})' # YYYYMMDD
        r')\b',
        re.IGNORECASE
    )

    potential_dates_str = date_pattern.findall(text)
    parsed_dates = set() # Use a set to store unique dates

    for date_str in potential_dates_str:
        # Clean up common issues, e.g., "1st" -> "1" before parsing for some formats
        # This part can be expanded. For now, just stripping.
        cleaned_date_str = date_str.strip()

        parsed_dt = parse_date_string(cleaned_date_str, formats)
        if parsed_dt:
            parsed_dates.add(parsed_dt)

    return sorted(list(parsed_dates))


def format_date(dt_obj: Union[date, datetime], fmt: str = "%Y-%m-%d") -> Optional[str]:
    """
    Formats a date or datetime object into a string.
    :param dt_obj: The date or datetime object.
    :param fmt: The target format string.
    """
    if not isinstance(dt_obj, (date, datetime)):
        return None
    try:
        return dt_obj.strftime(fmt)
    except ValueError: # Should not happen with valid date/datetime and standard formats
        return None

def is_valid_date(year: int, month: int, day: int) -> bool:
    """
    Checks if a given year, month, and day form a valid date.
    """
    try:
        date(year, month, day)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    print("--- Testing parse_date_string ---")
    dates_to_test = [
        "15/05/2024", "15-05-2024", "2024-05-15", "2024/05/15", "15.05.2024",
        "05/15/2024", "15 May 2024", "15 MAY 2024", "15th May 2024", # "15th" might fail with %d
        "20240515", "InvalidDate", None, "30/02/2024" # February 30th is invalid
    ]
    for dt_str in dates_to_test:
        parsed = parse_date_string(dt_str)
        print(f"Parsing '{dt_str}': {parsed} (Type: {type(parsed).__name__ if parsed else 'None'})")

    print("\n--- Testing find_and_parse_dates ---")
    text_with_dates = """
    Document created on 10/01/2023. Review by 2023-12-31.
    Meeting scheduled for 05 Feb 2024 and another one on 20.03.2024.
    Invoice date: 20231120. Invalid date: 99/99/9999.
    The event was on 1st April 2022. US style: 04/15/2022.
    """
    found_dates = find_and_parse_dates(text_with_dates)
    print(f"Text: \"{text_with_dates[:100]}...\"")
    print(f"Found and parsed dates: {found_dates}")

    text_no_dates = "This text contains no recognizable dates."
    no_dates_found = find_and_parse_dates(text_no_dates)
    print(f"\nText: \"{text_no_dates}\"")
    print(f"Found and parsed dates: {no_dates_found}")

    print("\n--- Testing format_date ---")
    today = date.today()
    now = datetime.now()
    print(f"Today ({today}) formatted as default: {format_date(today)}")
    print(f"Today ({today}) formatted as DD/MM/YYYY: {format_date(today, '%d/%m/%Y')}")
    print(f"Now ({now}) formatted as YYYY-MM-DD HH:MM:SS: {format_date(now, '%Y-%m-%d %H:%M:%S')}")
    print(f"Formatting None: {format_date(None)}")

    print("\n--- Testing is_valid_date ---")
    print(f"Is 2023-12-15 valid? {is_valid_date(2023, 12, 15)}") # True
    print(f"Is 2023-02-29 valid (non-leap)? {is_valid_date(2023, 2, 29)}") # False
    print(f"Is 2024-02-29 valid (leap)? {is_valid_date(2024, 2, 29)}") # True
    print(f"Is 2023-13-01 valid (invalid month)? {is_valid_date(2023, 13, 1)}") # False
    print(f"Is 2023-04-31 valid (invalid day for Apr)? {is_valid_date(2023, 4, 31)}") # False
