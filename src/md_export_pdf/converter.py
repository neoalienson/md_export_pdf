# src/md_export_pdf/converter.py

import logging
import markdown
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import os
from typing import Optional, Type
import fitz  # Import fitz for PyMuPDF operations
from .html_generator import convert_markdown_to_html
from .pdf_postprocessors.base import PdfPostProcessor
from .pdf_postprocessors.pymupdf_header import PyMuPdfHeaderPostProcessor
from .pdf_postprocessors.pymupdf_footer import PyMuPdfFooterPostProcessor
from .pdf_postprocessors.dummy import DummyPostProcessor
from .pdf_postprocessors.data_classification_watermark import (
    DataClassificationWatermarkPostProcessor,
)
from .pdf_postprocessors.draft_watermark import DraftWatermarkPostProcessor
from .pdf_postprocessors.metadata_postprocessor import MetadataPostProcessor
from .html_preprocessors.weasyprint_header_footer import apply_weasyprint_header_footer
from .html_preprocessors.cover_page_processor import apply_cover_page

logger = logging.getLogger(__name__)


class MarkdownToPdfConverter:
    def __init__(
        self,
        input_file,
        output_file,
        css_file=None,
        header_content=None,
        header_file=None,
        header_css=None,
        footer_content=None,
        footer_file=None,
        footer_css=None,
        cover_page_file=None,
        cover_css=None,
        use_pymupdf_header: bool = False,
        use_pymupdf_footer: bool = False,
        use_dummy_postprocessor: bool = False,
    ):
        self.input_file = input_file
        self.output_file = output_file
        self.css_file = css_file
        self.header_content = header_content
        self.header_file = header_file
        self.header_css = header_css
        self.footer_content = footer_content
        self.footer_file = footer_file
        self.footer_css = footer_css
        self.cover_page_file = cover_page_file
        self.cover_css = cover_css
        self.use_pymupdf_header = use_pymupdf_header
        self.use_pymupdf_footer = use_pymupdf_footer
        self.use_dummy_postprocessor = use_dummy_postprocessor
        self.post_processor: Optional[PdfPostProcessor] = None  # New attribute

    def _read_file_content(self, file_path, markdown_convert: bool = True):
        logger.debug(
            f"Reading file content from: {file_path}, Markdown conversion: {markdown_convert}"
        )
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"File not found or path is empty: {file_path}")
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # If it's a markdown file and markdown_convert is True, convert to HTML
        if markdown_convert and file_path.lower().endswith((".md", ".markdown")):
            logger.debug(f"Converting Markdown content from {file_path} to HTML.")
            return markdown.markdown(content)
        logger.debug(f"Returning plain content from {file_path}.")
        return content  # Assume HTML or plain text

    def _read_markdown(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            return f.read()

    def _apply_html_template(self, html_content):
        logger.debug("Applying HTML template...")
        # Create a basic HTML structure for WeasyPrint
        template_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Markdown to PDF</title>
        </head>
        <body>
            <div class="content">
                {html_content}
            </div>
        </body>
        </html>
        """

        soup = BeautifulSoup(template_html, "html.parser")
        logger.debug("BeautifulSoup object created from template.")

        # Apply cover page
        apply_cover_page(soup, self)

        # Apply WeasyPrint headers and footers
        apply_weasyprint_header_footer(soup, self)

        logger.debug(
            "HTML template application complete. Returning string representation."
        )
        return str(soup)

    def convert(self):
        logger.info(
            f"Starting PDF conversion for '{self.input_file}' to '{self.output_file}'"
        )
        md_content = self._read_markdown()
        logger.debug("Markdown content read.")
        html_content, front_matter_data = convert_markdown_to_html(md_content)
        logger.debug("Markdown converted to HTML.")
        final_html = self._apply_html_template(html_content)
        logger.debug("HTML template applied.")

        # Debug: Save final_html to a temporary file
        debug_html_path = "debug_output.html"
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        logger.debug(f"Saved final HTML to {debug_html_path} for debugging.")

        # Convert HTML to PDF using WeasyPrint
        logger.info("Starting WeasyPrint conversion...")
        html_doc = HTML(string=final_html, base_url=os.path.dirname(self.input_file))

        stylesheets = []
        if self.css_file and os.path.exists(self.css_file):
            stylesheets.append(CSS(filename=self.css_file))
            logger.debug(f"Added custom CSS: {self.css_file}")

        if not self.use_pymupdf_header:
            if self.header_css and os.path.exists(self.header_css):
                stylesheets.append(CSS(filename=self.header_css))
                logger.debug(f"Added header CSS: {self.header_css}")
        if not self.use_pymupdf_footer:
            if self.footer_css and os.path.exists(self.footer_css):
                stylesheets.append(CSS(filename=self.footer_css))
                logger.debug(f"Added footer CSS: {self.footer_css}")

        if self.cover_page_file and self.cover_css and os.path.exists(self.cover_css):
            stylesheets.append(CSS(filename=self.cover_css))
            logger.debug(f"Added cover page CSS: {self.cover_css}")

        # Add default CSS for basic styling
        default_css_path = os.path.join(
            os.path.dirname(__file__), "styles", "default.css"
        )
        if os.path.exists(default_css_path):
            stylesheets.append(CSS(filename=default_css_path))
            logger.debug(f"Added default CSS: {default_css_path}")

        try:
            html_doc.write_pdf(self.output_file, stylesheets=stylesheets)
            logger.info(
                f"Successfully converted '{self.input_file}' to '{self.output_file}' using WeasyPrint."
            )
        except Exception as e:
            logger.error(f"An error occurred during WeasyPrint conversion: {e}")
            import traceback

            logger.error(traceback.format_exc())
            raise  # Re-raise the exception to stop execution

        post_processors = [
            PyMuPdfHeaderPostProcessor,
            PyMuPdfFooterPostProcessor,
            DummyPostProcessor,
            DataClassificationWatermarkPostProcessor,
            DraftWatermarkPostProcessor,
            MetadataPostProcessor,
        ]

        for pp_class in sorted(post_processors, key=lambda x: x(self).priority):
            pp_instance = pp_class(self)
            if pp_instance.should_apply(self, front_matter_data):
                logger.info(f"Applying PDF post-processor: {pp_class.__name__}...")
                options = pp_instance.get_process_options(self, front_matter_data)
                pp_instance.process(self.output_file, options)
                logger.info(f"PDF post-processor {pp_class.__name__} applied.")
            else:
                logger.debug(f"PDF post-processor {pp_class.__name__} skipped.")
