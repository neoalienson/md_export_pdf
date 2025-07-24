import os
import fitz
import markdown
from . import utils
from . import html_generator
from . import template_renderer
from . import logger
from . import style_manager

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

        # Process cover page separately if provided
        cover_page_html = None
        if self.cover_page_file:
            cover_page_md_content = utils.read_file_content(self.cover_page_file)
            if cover_page_md_content:
                md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'attr_list', 'tables'])
                cover_page_html = md.convert(cover_page_md_content)
                logger.info("Cover page HTML generated.")
            else:
                logger.warning(f"Cover page file not found or empty: {self.cover_page_file}")

        # Generate main content HTML
        main_html = template_renderer.apply_html_template(
            html_content=html_content,
            header_content=self.header_content,
            header_file=self.header_file,
            footer_content=self.footer_content,
            footer_file=self.footer_file,
            cover_page_file=None  # Cover page handled separately
        )
        logger.debug("Main HTML template applied.")

        # Debug: Save main_html to a temporary file
        debug_html_path = self.output_file.replace(".pdf", ".debug.html")
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(main_html)
        logger.info(f"Debug HTML saved to: {debug_html_path}")

        # Load CSS content
        all_stylesheets = style_manager.get_stylesheets(
            self.css_file,
            self.header_css,
            self.footer_css,
            self.cover_css # Still pass cover_css for general styling if needed
        )
        combined_css_content = ""
        for css_string in all_stylesheets:
            combined_css_content += css_string + "\n"

        doc = fitz.open()  # new PDF document
        margin = 72  # 1 inch margin (72 points per inch)

        # Render cover page if exists
        if cover_page_html:
            cover_page = doc.new_page()
            r_cover = cover_page.rect
            r_cover.x0 += margin
            r_cover.y0 += margin
            r_cover.x1 -= margin
            r_cover.y1 -= margin
            cover_page.insert_htmlbox(r_cover, cover_page_html, css=combined_css_content)
            logger.info("Cover page rendered.")

        # Render main content
        main_page = doc.new_page()
        r_main = main_page.rect
        r_main.x0 += margin
        r_main.y0 += margin
        r_main.x1 -= margin
        r_main.y1 -= margin
        main_page.insert_htmlbox(r_main, main_html, css=combined_css_content)
        logger.info("Main content rendered.")

        try:
            doc.save(self.output_file)
        except Exception as e:
            logger.error(f"Error converting HTML to PDF with PyMuPDF: {e}")
            raise
        logger.info(f"Successfully converted '{self.input_file}' to '{self.output_file}'")