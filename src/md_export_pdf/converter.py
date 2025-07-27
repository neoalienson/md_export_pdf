# src/md_export_pdf/converter.py

import logging
import markdown
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import os
from typing import Optional, Type
import fitz # Import fitz for PyMuPDF operations
from .md_processor.markdown import convert_markdown_to_html
from .md_processor.front_matter import extract_front_matter
from .pdf_postprocessors.base import PdfPostProcessor
from .pdf_postprocessors.pymupdf_header import PyMuPdfHeaderPostProcessor
from .pdf_postprocessors.pymupdf_footer import PyMuPdfFooterPostProcessor
from .pdf_postprocessors.dummy import DummyPostProcessor
from .pdf_postprocessors.data_classification_watermark import DataClassificationWatermarkPostProcessor
from .pdf_postprocessors.draft_watermark import DraftWatermarkPostProcessor

logger = logging.getLogger(__name__)

class MarkdownToPdfConverter:
    def __init__(self, input_file, output_file, css_file=None, header_content=None, header_file=None, header_css=None, footer_content=None, footer_file=None, footer_css=None, cover_page_file=None, cover_css=None, use_pymupdf_header: bool = False, use_pymupdf_footer: bool = False, use_dummy_postprocessor: bool = False):
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
        self.post_processor: Optional[PdfPostProcessor] = None # New attribute

    def _read_file_content(self, file_path, markdown_convert: bool = True):
        logger.debug(f"Reading file content from: {file_path}, Markdown conversion: {markdown_convert}")
        if not file_path or not os.path.exists(file_path):
            logger.warning(f"File not found or path is empty: {file_path}")
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # If it's a markdown file and markdown_convert is True, convert to HTML
        if markdown_convert and file_path.lower().endswith(('.md', '.markdown')):
            logger.debug(f"Converting Markdown content from {file_path} to HTML.")
            return markdown.markdown(content)
        logger.debug(f"Returning plain content from {file_path}.")
        return content # Assume HTML or plain text

    def _read_markdown(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _convert_cover_page_to_html(self):
        if not self.cover_page_file or not os.path.exists(self.cover_page_file):
            return ""
        with open(self.cover_page_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        # Simple Markdown conversion for cover page, no TOC or Mermaid processing
        return markdown.markdown(md_content)

    

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

        soup = BeautifulSoup(template_html, 'html.parser')
        logger.debug("BeautifulSoup object created from template.")

        # Insert cover page if provided
        cover_page_html = self._convert_cover_page_to_html()
        if cover_page_html:
            logger.debug("Cover page HTML generated. Inserting into soup.")
            cover_page_div = soup.new_tag("div", id="cover-page", class_="cover-page")
            cover_page_div.append(BeautifulSoup(cover_page_html, 'html.parser'))
            soup.body.insert(0, cover_page_div)

        # Populate header content if using WeasyPrint for headers
        if not self.use_pymupdf_header:
            logger.debug("Populating WeasyPrint header content.")
            header_html_content = self.header_content
            if self.header_file:
                file_content = self._read_file_content(self.header_file)
                if file_content is not None:
                    header_html_content = file_content

            if header_html_content:
                # Create a div for the header content and insert it at the beginning of the body
                header_element = soup.new_tag("div", id="pdf-header", class_="document-header")
                header_element.append(BeautifulSoup(header_html_content, 'html.parser'))
                soup.body.insert(1, header_element) # Insert after cover page if present, or at beginning
                logger.debug("WeasyPrint header content appended.")

        # Populate footer content with page number placeholders if using WeasyPrint for footers
        if not self.use_pymupdf_footer:
            logger.debug("Populating WeasyPrint footer content.")
            footer_html_content = self.footer_content
            if self.footer_file:
                file_content = self._read_file_content(self.footer_file)
                if file_content is not None:
                    footer_html_content = file_content

            if footer_html_content:
                # Replace placeholders for page numbering
                footer_html = footer_html_content.replace('{page_num}', '<span class="page-number"></span>')
                footer_html = footer_html.replace('{total_pages}', '<span class="total-pages"></span>')

                # Create a div for the footer content and append it to the body
                footer_element = soup.new_tag("div", id="pdf-footer", class_="document-footer")
                footer_element.append(BeautifulSoup(footer_html, 'html.parser'))
                soup.body.append(footer_element)
                logger.debug("WeasyPrint footer content appended.")

        logger.debug("HTML template application complete. Returning string representation.")
        return str(soup)

    

    def convert(self):
        logger.info(f"Starting PDF conversion for '{self.input_file}' to '{self.output_file}'")
        md_content = self._read_markdown()
        logger.debug("Markdown content read.")
        md_content, front_matter_data = extract_front_matter(md_content)
        html_content = convert_markdown_to_html(md_content)
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
        default_css_path = os.path.join(os.path.dirname(__file__), 'styles', 'default.css')
        if os.path.exists(default_css_path):
            stylesheets.append(CSS(filename=default_css_path))
            logger.debug(f"Added default CSS: {default_css_path}")

        try:
            html_doc.write_pdf(self.output_file, stylesheets=stylesheets)
            logger.info(f"Successfully converted '{self.input_file}' to '{self.output_file}' using WeasyPrint.")
        except Exception as e:
            logger.error(f"An error occurred during WeasyPrint conversion: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise # Re-raise the exception to stop execution

        # Determine and initialize PDF post-processor
        logger.debug(f"PyMuPDF header toggle: {self.use_pymupdf_header}")
        logger.debug(f"PyMuPDF footer toggle: {self.use_pymupdf_footer}")
        logger.debug(f"Header content: '{self.header_content}'")
        logger.debug(f"Footer content: '{self.footer_content}'")
        logger.debug(f"Header file: '{self.header_file}'")
        logger.debug(f"Footer file: '{self.footer_file}'")
        if self.use_pymupdf_header and (self.header_content or self.header_file):
            logger.info("Starting PyMuPDF header post-processing...")
            header_text = self.header_content or (self._read_file_content(self.header_file, markdown_convert=False) if self.header_file else "")
            header_post_processor = PyMuPdfHeaderPostProcessor(self)
            header_post_processor.apply_modifications(self.output_file, {'header_text': header_text, 'use_header': True})
            logger.info("PyMuPDF header post-processing complete.")
        else:
            logger.info("PyMuPDF header post-processing skipped (not toggled or no content).")

        if self.use_pymupdf_footer and (self.footer_content or self.footer_file):
            logger.info("Starting PyMuPDF footer post-processing...")
            footer_text = self.footer_content or (self._read_file_content(self.footer_file, markdown_convert=False) if self.footer_file else "")
            footer_post_processor = PyMuPdfFooterPostProcessor(self)
            footer_post_processor.apply_modifications(self.output_file, {'footer_text': footer_text, 'use_footer': True})
            logger.info("PyMuPDF footer post-processing complete.")
        else:
            logger.info("PyMuPDF footer post-processing skipped (not toggled or no content).")

        if front_matter_data.get('draft', False):
            logger.info("Starting DraftWatermark post-processing (draft mode detected)...")
            draft_watermark_post_processor = DraftWatermarkPostProcessor(self)
            draft_watermark_post_processor.apply_modifications(self.output_file, {})
            logger.info("DraftWatermark post-processing complete.")
        else:
            logger.info("DraftWatermark post-processing skipped (not in draft mode).")

        data_classification = front_matter_data.get('data_classification')
        if data_classification:
            logger.info(f"Starting DataClassificationWatermark post-processing (classification: {data_classification})...")
            data_classification_watermark_post_processor = DataClassificationWatermarkPostProcessor(self)
            data_classification_watermark_post_processor.apply_modifications(self.output_file, {'data_classification': data_classification})
            logger.info("DataClassificationWatermark post-processing complete.")
        else:
            logger.info("DataClassificationWatermark post-processing skipped (no classification specified).")

        # Apply metadata from front matter
        metadata_list = front_matter_data.get('metadata', [])
        if metadata_list:
            logger.info("Applying metadata from front matter...")
            doc = fitz.open(self.output_file)
            pdf_metadata = doc.metadata
            # Define a mapping of valid PyMuPDF metadata keys
            # PyMuPDF expects keys like 'author', 'title', 'subject', 'keywords', 'creator', 'producer', 'creationDate', 'modDate'
            valid_pymupdf_keys = ['author', 'title', 'subject', 'keywords', 'creator', 'producer', 'creationdate', 'moddate']

            for item in metadata_list:
                for key, value in item.items():
                    lower_key = key.lower()
                    if lower_key in valid_pymupdf_keys:
                        pdf_metadata[lower_key] = value
                    else:
                        logger.warning(f"Skipping unsupported PDF metadata key: '{key}'. PyMuPDF only supports: {', '.join(valid_pymupdf_keys)}")
            doc.set_metadata(pdf_metadata)
            doc.saveIncr() # Save changes incrementally
            doc.close()
            logger.info("Metadata applied successfully.")
        else:
            logger.info("No metadata found in front matter to apply.")

