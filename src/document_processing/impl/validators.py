from src.document_processing.core.base import Validator
from typing import Any, Dict, List
import re

class DataLengthValidator(Validator):
    """
    Validates the length of a data field.
    Rules: {"min_length": int, "max_length": int}
    """
    def validate(self, data: Any, rules: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        data_str = str(data) # Ensure data is string for length check

        min_len = rules.get("min_length")
        if min_len is not None and len(data_str) < min_len:
            errors.append(f"Data '{data_str}' is shorter than minimum length {min_len}.")

        max_len = rules.get("max_length")
        if max_len is not None and len(data_str) > max_len:
            errors.append(f"Data '{data_str}' is longer than maximum length {max_len}.")

        # print(f"DataLengthValidator: Validated '{data_str}' against rules {rules}. Errors: {errors}")
        return errors

class RegexValidator(Validator):
    """
    Validates data against a regex pattern.
    Rules: {"pattern": str (regex)}
    """
    def validate(self, data: Any, rules: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        pattern = rules.get("pattern")

        if not pattern:
            errors.append("Regex pattern not provided in rules.")
            return errors

        try:
            if not re.match(pattern, str(data)):
                errors.append(f"Data '{data}' does not match pattern '{pattern}'.")
        except re.error as e:
            errors.append(f"Invalid regex pattern '{pattern}': {e}")

        # print(f"RegexValidator: Validated '{data}' against pattern '{pattern}'. Errors: {errors}")
        return errors

class DateFormatValidator(Validator):
    """
    Validates if a string is in a specific date format (e.g., YYYY-MM-DD).
    Rules: {"format": "YYYY-MM-DD"} (Currently only supports this one format)
    """
    def validate(self, data: Any, rules: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        date_format = rules.get("format")

        if date_format == "YYYY-MM-DD":
            if not isinstance(data, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", data):
                errors.append(f"Date '{data}' is not in YYYY-MM-DD format.")
            else:
                # Basic structural validation, not logical (e.g., 2023-13-01 would pass regex but is invalid date)
                # For full date validation, datetime.strptime would be used in a try-except block.
                try:
                    year, month, day = map(int, data.split('-'))
                    if not (1 <= month <= 12 and 1 <= day <= 31): # Basic sanity check
                         errors.append(f"Date '{data}' contains invalid month or day numbers.")
                    # Further checks for days in month, leap years etc. could be added here.
                except ValueError:
                     errors.append(f"Date '{data}' is not a valid date structure.")

        else:
            errors.append(f"Unsupported date format rule: {date_format}. Only 'YYYY-MM-DD' is supported by this validator.")

        # print(f"DateFormatValidator: Validated '{data}' against format '{date_format}'. Errors: {errors}")
        return errors

class AllowedValuesValidator(Validator):
    """
    Validates if the data is one of the allowed values.
    Rules: {"allowed_values": List[Any]}
    """
    def validate(self, data: Any, rules: Dict[str, Any]) -> List[str]:
        errors: List[str] = []
        allowed_values = rules.get("allowed_values")

        if allowed_values is None:
            errors.append("Allowed values not provided in rules.")
            return errors

        if not isinstance(allowed_values, list):
            errors.append("Allowed values rule must be a list.")
            return errors

        if data not in allowed_values:
            errors.append(f"Data '{data}' is not in the list of allowed values: {allowed_values}.")

        return errors
