from abc import ABC, abstractmethod
from typing import Dict, Any
from ..base_processor import BaseProcessor, ProcessorType


class PdfPostProcessor(BaseProcessor):
    def __init__(self, converter_instance: Any, priority: int = 0):
        super().__init__(priority, ProcessorType.PDF_POSTPROCESSOR)
        self.converter = converter_instance

    @abstractmethod
    @abstractmethod
    def should_apply(self, converter_instance: Any, front_matter_data: Dict) -> bool:
        """
        Determines if this post-processor should be applied based on converter settings
        and front matter data.
        """
        pass

    @abstractmethod
    def get_process_options(
        self, converter_instance: Any, front_matter_data: Dict
    ) -> Dict:
        """
        Returns a dictionary of options specific to this post-processor.
        """
        pass

    @abstractmethod
    def process(self, pdf_path: str, options: Dict) -> None:
        """
        Applies modifications to the PDF at the given path.
        :param pdf_path: The absolute path to the PDF file to modify.
        :param options: A dictionary of options specific to the post-processor.
        """
        pass
