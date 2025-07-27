from abc import ABC, abstractmethod
from typing import Dict, Any

class PdfPostProcessor(ABC):
    def __init__(self, converter_instance: Any):
        """
        Initializes the PDF post-processor.
        :param converter_instance: A reference to the MarkdownToPdfConverter instance,
                                   allowing access to its properties (e.g., cover_page_file).
        """
        self.converter = converter_instance

    @abstractmethod
    def apply_modifications(self, pdf_path: str, options: Dict) -> None:
        """
        Applies modifications to the PDF at the given path.
        :param pdf_path: The absolute path to the PDF file to modify.
        :param options: A dictionary of options specific to the post-processor.
        """
        pass