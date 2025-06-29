from abc import ABC, abstractmethod

class BaseValidator(ABC):
    def __init__(self, data: dict):
        self.data = data

    @abstractmethod
    def validate(self) -> dict:
        """
        Validates the extracted data against predefined rules.
        Should be implemented by subclasses for specific document types.
        """
        pass
