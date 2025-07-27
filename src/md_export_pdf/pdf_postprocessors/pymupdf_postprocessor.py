import fitz
import os
import logging
import traceback
from typing import Dict, Any

from .base import PdfPostProcessor

class PyMuPdfPostProcessor(PdfPostProcessor):
    def __init__(self, converter_instance: Any):
        super().__init__(converter_instance)
        self.logger = logging.getLogger(__name__)

    def apply_modifications(self, pdf_path: str, options: Dict) -> None:
        header_text = options.get('header_text', '')
        footer_text = options.get('footer_text', '')
        use_header = options.get('use_header', False)
        use_footer = options.get('use_footer', False)
        
        font_name = "Helvetica" # Using a standard base 14 font for robustness

        self.logger.debug(f"PyMuPdfPostProcessor: Applying modifications to {pdf_path}")
        self.logger.debug(f"Header text: '{header_text}', Footer text: '{footer_text}'")
        self.logger.debug(f"Use header: {use_header}, Use footer: {use_footer}")

        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        self.logger.debug(f"Total pages in PDF: {num_pages}")

        for i, page in enumerate(doc):
            self.logger.debug(f"Processing page {i+1} of {num_pages}")
            
            if self.converter.cover_page_file and i == 0:
                self.logger.debug(f"Skipping cover page {i+1} for header/footer.")
                continue

            if use_header and header_text:
                self.logger.debug(f"Attempting to add PyMuPDF header to page {i+1}. Text: '{header_text}'")
                try:
                    page.insert_text((50, 50), header_text, fontname=font_name, fontsize=10)
                    self.logger.debug(f"PyMuPDF header added successfully to page {i+1}.")
                except Exception as e:
                    self.logger.error(f"Error adding PyMuPDF header to page {i+1}: {e}")
                    self.logger.error(traceback.format_exc())

            if use_footer and footer_text:
                self.logger.debug(f"Attempting to add PyMuPDF footer to page {i+1}. Text: '{footer_text}'")
                try:
                    footer_y = page.rect.height - 50
                    page.insert_text((50, footer_y), footer_text.format(page_num=i + 1, total_pages=num_pages), fontname=font_name, fontsize=10)
                    self.logger.debug(f"PyMuPDF footer added successfully to page {i+1}.")
                except Exception as e:
                    self.logger.error(f"Error adding PyMuPDF footer to page {i+1}: {e}")
                    self.logger.error(traceback.format_exc())
        
        self.logger.debug(f"Saving modified PDF to {pdf_path}")
        temp_output_path = pdf_path + ".tmp"
        doc.save(temp_output_path)
        doc.close()
        os.replace(temp_output_path, pdf_path)
        self.logger.debug(f"PDF saved and replaced successfully.")