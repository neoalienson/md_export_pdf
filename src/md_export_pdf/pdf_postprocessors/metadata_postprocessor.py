import fitz
import logging
import os
from typing import Dict, Any

from .base import PdfPostProcessor

logger = logging.getLogger(__name__)


class MetadataPostProcessor(PdfPostProcessor):
    def __init__(self, converter_instance: Any, priority: int = 50):
        super().__init__(converter_instance, priority)
        self.logger = logging.getLogger(__name__)

    def process(self, pdf_path: str, options: Dict) -> None:
        metadata_list = options.get("metadata_list", [])
        if not metadata_list:
            self.logger.info(
                "No metadata found to apply. Skipping MetadataPostProcessor."
            )
            return

        self.logger.info("Applying metadata from front matter...")
        doc = fitz.open(pdf_path)
        pdf_metadata = doc.metadata

        # Define a mapping of valid PyMuPDF metadata keys
        valid_pymupdf_keys = [
            "author",
            "title",
            "subject",
            "keywords",
            "creator",
            "producer",
            "creationdate",
            "moddate",
        ]

        for item in metadata_list:
            for key, value in item.items():
                lower_key = key.lower()
                if lower_key in valid_pymupdf_keys:
                    pdf_metadata[lower_key] = value
                else:
                    self.logger.warning(
                        f"Skipping unsupported PDF metadata key: '{key}'. PyMuPDF only supports: {', '.join(valid_pymupdf_keys)}"
                    )

        doc.set_metadata(pdf_metadata)
        doc.saveIncr()  # Save changes incrementally
        doc.close()
        self.logger.info("Metadata applied successfully.")
