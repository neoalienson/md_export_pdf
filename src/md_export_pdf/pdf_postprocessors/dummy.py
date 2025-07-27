import logging
from typing import Dict, Any

from .base import PdfPostProcessor


class DummyPostProcessor(PdfPostProcessor):
    def __init__(self, converter_instance: Any, priority: int = 0):
        super().__init__(converter_instance, priority)
        self.logger = logging.getLogger(__name__)
        self.logger.info("DummyPostProcessor initialized.")

    def should_apply(self, converter_instance: Any, front_matter_data: Dict) -> bool:
        return converter_instance.use_dummy_postprocessor

    def process(self, pdf_path: str, options: Dict) -> None:
        self.logger.info(
            f"DummyPostProcessor: apply_modifications called for {pdf_path} with options: {options}"
        )
        # This dummy processor does nothing to the PDF file.
