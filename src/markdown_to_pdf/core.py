import os
import fitz
from . import utils
from . import html_generator
from . import template_renderer
from . import logger

class MarkdownToPdfConverter:
    def __init__(self, input_file, output_file, css_file=None, header_content=None, header_file=None, header_css=None, footer_content=None, footer_file=None, footer_css=None, cover_page_file=None, cover_css=None):
        logger.debug(f"Initializing MarkdownToPdfConverter with input_file={input_file}, output_file={output_file}, css_file={css_file}")
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

    def convert(self):
        logger.info(f"Starting conversion of '{self.input_file}' to '{self.output_file}'")
        md_content = utils.read_file_content(self.input_file)
        if md_content is None:
            logger.error(f"Input Markdown file not found: {self.input_file}")
            raise FileNotFoundError(f"Input Markdown file not found: {self.input_file}")
        logger.debug(f"Markdown content read from {self.input_file}")

        html_content = html_generator.convert_markdown_to_html(md_content)
        logger.debug("Markdown converted to HTML.")

        final_html = template_renderer.apply_html_template(
            html_content=html_content,
            header_content=self.header_content,
            header_file=self.header_file,
            footer_content=self.footer_content,
            footer_file=self.footer_file,
            cover_page_file=self.cover_page_file
        )
        logger.debug("HTML template applied.")

        # Debug: Save final_html to a temporary file
        debug_html_path = self.output_file.replace(".pdf", ".debug.html")
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        logger.info(f"Debug HTML saved to: {debug_html_path}")

        # Convert HTML to PDF using PyMuPDF
        doc = fitz.open()  # new PDF document
        page = doc.new_page()  # new page

        # Load CSS content if available
        css_content = ""
        if self.css_file and os.path.exists(self.css_file):
            try:
                with open(self.css_file, "r", encoding="utf-8") as f:
                    css_content = f.read()
            except Exception as e:
                logger.warning(f"Could not read CSS file {self.css_file}: {e}")

        # Insert HTML with CSS
        try:
            # The rect defines the area where the HTML content will be rendered.
            # We use an inset rect to create margins.
            margin = 72  # 1 inch margin (72 points per inch)
            r = page.rect
            r.x0 += margin
            r.y0 += margin
            r.x1 -= margin
            r.y1 -= margin
            page.insert_htmlbox(r, final_html, css=css_content)
            doc.save(self.output_file)
        except Exception as e:
            logger.error(f"Error converting HTML to PDF with PyMuPDF: {e}")
            raise
        logger.info(f"Successfully converted '{self.input_file}' to '{self.output_file}'")