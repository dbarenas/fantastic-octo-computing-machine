from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    def __init__(self, text: str):
        self.text = text

    @abstractmethod
    def extract(self) -> dict:
        """
        Extracts relevant information from the document text.
        Should be implemented by subclasses for specific document types.
        """
        pass
