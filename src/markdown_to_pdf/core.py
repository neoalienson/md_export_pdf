import os
from weasyprint import HTML
from . import utils
from . import html_generator
from . import template_renderer
from . import style_manager

class MarkdownToPdfConverter:
    def __init__(self, input_file, output_file, css_file=None, header_content=None, header_file=None, header_css=None, footer_content=None, footer_file=None, footer_css=None, cover_page_file=None, cover_css=None):
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
        md_content = utils.read_file_content(self.input_file)
        if md_content is None:
            raise FileNotFoundError(f"Input Markdown file not found: {self.input_file}")

        html_content = html_generator.convert_markdown_to_html(md_content)

        final_html = template_renderer.apply_html_template(
            html_content=html_content,
            header_content=self.header_content,
            header_file=self.header_file,
            footer_content=self.footer_content,
            footer_file=self.footer_file,
            cover_page_file=self.cover_page_file
        )

        # Convert HTML to PDF using WeasyPrint
        html_doc = HTML(string=final_html, base_url=os.path.dirname(self.input_file))

        stylesheets = style_manager.get_stylesheets(
            css_file=self.css_file,
            header_css=self.header_css,
            footer_css=self.footer_css,
            cover_css=self.cover_css
        )

        html_doc.write_pdf(self.output_file, stylesheets=stylesheets)
        print(f"Successfully converted '{self.input_file}' to '{self.output_file}'")