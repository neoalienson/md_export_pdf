# src/md_export_pdf/converter.py

import logging
import markdown
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import os
from typing import Optional, Type
import fitz # Import fitz for PyMuPDF operations
from md_export_pdf.markdown_processor import convert_markdown_to_html
from .pdf_postprocessors.base import PdfPostProcessor
from .pdf_postprocessors.pymupdf_postprocessor import PyMuPdfPostProcessor
from .pdf_postprocessors.dummy_postprocessor import DummyPostProcessor

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
        self.use_dummy_postprocessor = use_dummy_postprocessor # New attribute
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

    def _add_pymupdf_header_footer(self, pdf_path, header_text, footer_text):
        logger.debug(f"_add_pymupdf_header_footer called for PDF: {pdf_path}")
        logger.debug(f"Header text: '{header_text}', Footer text: '{footer_text}'")
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        logger.debug(f"Total pages in PDF: {num_pages}")

        for i, page in enumerate(doc):
            logger.debug(f"Processing page {i+1} of {num_pages}")
            # Skip cover page for header/footer
            if self.cover_page_file and i == 0:
                logger.debug(f"Skipping cover page {i+1} for header/footer.")
                continue

            # Register a standard font for robustness
            try:
                # Use a standard base 14 font like Helvetica
                font_name = "Helvetica"
                # Ensure the font is available in the PDF
                # PyMuPDF automatically handles embedding for base 14 fonts
            except Exception as e:
                logger.error(f"Error registering font for PyMuPDF: {e}")
                logger.error(traceback.format_exc())
                # Fallback or re-raise if font is critical

            # Add header
            if self.use_pymupdf_header and header_text:
                logger.debug(f"Attempting to add PyMuPDF header to page {i+1}. Text: '{header_text}'")
                try:
                    page.insert_text((50, 50), header_text, fontname="helv", fontsize=10)
                    logger.debug(f"PyMuPDF header added successfully to page {i+1}.")
                except Exception as e:
                    logger.error(f"Error adding PyMuPDF header to page {i+1}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())

            # Add footer
            if self.use_pymupdf_footer and footer_text:
                logger.debug(f"Attempting to add PyMuPDF footer to page {i+1}. Text: '{footer_text}'")
                try:
                    footer_y = page.rect.height - 50
                    page.insert_text((50, footer_y), footer_text.format(page_num=i + 1, total_pages=num_pages), fontname="helv", fontsize=10)
                    logger.debug(f"PyMuPDF footer added successfully to page {i+1}.")
                except Exception as e:
                    logger.error(f"Error adding PyMuPDF footer to page {i+1}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
        
        logger.debug(f"Saving modified PDF to {pdf_path}")
        temp_output_path = pdf_path + ".tmp"
        doc.save(temp_output_path)
        doc.close()
        os.replace(temp_output_path, pdf_path) # Replace original file with modified one
        logger.debug(f"PDF saved and replaced successfully.")

    def convert(self):
        logger.info(f"Starting PDF conversion for '{self.input_file}' to '{self.output_file}'")
        md_content = self._read_markdown()
        logger.debug("Markdown content read.")
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
        if (self.use_pymupdf_header and (self.header_content or self.header_file)) or \
           (self.use_pymupdf_footer and (self.footer_content or self.footer_file)):
            logger.info("Starting PyMuPDF header/footer post-processing...")
            header_text = self.header_content or (self._read_file_content(self.header_file, markdown_convert=False) if self.header_file else "")
            footer_text = self.footer_content or (self._read_file_content(self.footer_file, markdown_convert=False) if self.footer_file else "")
            self._add_pymupdf_header_footer(self.output_file, header_text, footer_text)
            logger.info("PyMuPDF header/footer post-processing complete.")
        else:
            logger.info("PyMuPDF header/footer post-processing skipped (not toggled or no content).")

