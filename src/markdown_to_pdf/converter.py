# src/markdown_to_pdf/converter.py

import markdown
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup
import os
from .markdown_processor import convert_markdown_to_html

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

    def _read_file_content(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # If it's a markdown file, convert to HTML
        if file_path.lower().endswith(('.md', '.markdown')):
            return markdown.markdown(content)
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
        # Create a basic HTML structure for WeasyPrint
        # Include dedicated divs for header and footer that are always present
        template_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Markdown to PDF</title>
        </head>
        <body>
            <div id="pdf-header" class="document-header"></div>
            <div class="content">
                {html_content}
            </div>
            <div id="pdf-footer" class="document-footer"></div>
        </body>
        </html>
        """
        soup = BeautifulSoup(template_html, 'html.parser')

        # Insert cover page if provided
        cover_page_html = self._convert_cover_page_to_html()
        if cover_page_html:
            cover_page_div = soup.new_tag("div", id="cover-page", class_="cover-page")
            cover_page_div.append(BeautifulSoup(cover_page_html, 'html.parser'))
            soup.body.insert(0, cover_page_div)

        # Populate header content
        header_html_content = self.header_content
        if self.header_file:
            file_content = self._read_file_content(self.header_file)
            if file_content is not None:
                header_html_content = file_content

        if header_html_content:
            soup.find(id="pdf-header").append(BeautifulSoup(header_html_content, 'html.parser'))

        # Populate footer content with page number placeholders
        footer_html_content = self.footer_content
        if self.footer_file:
            file_content = self._read_file_content(self.footer_file)
            if file_content is not None:
                footer_html_content = file_content

        if footer_html_content:
            # Replace placeholders for page numbering
            footer_html = footer_html_content.replace('{page_num}', '<span class="page-number"></span>')
            footer_html = footer_html.replace('{total_pages}', '<span class="total-pages"></span>')

            footer_element = soup.find(id="pdf-footer")
            footer_element.append(BeautifulSoup(footer_html, 'html.parser'))

        return str(soup)

    def convert(self):
        md_content = self._read_markdown()
        html_content = convert_markdown_to_html(md_content)
        final_html = self._apply_html_template(html_content)

        # Convert HTML to PDF using WeasyPrint
        html_doc = HTML(string=final_html, base_url=os.path.dirname(self.input_file))

        stylesheets = []
        if self.css_file and os.path.exists(self.css_file):
            stylesheets.append(CSS(filename=self.css_file))

        if self.header_css and os.path.exists(self.header_css):
            stylesheets.append(CSS(filename=self.header_css))

        if self.footer_css and os.path.exists(self.footer_css):
            stylesheets.append(CSS(filename=self.footer_css))

        if self.cover_page_file and self.cover_css and os.path.exists(self.cover_css):
            stylesheets.append(CSS(filename=self.cover_css))

        # Add default CSS for basic styling and header/footer positioning
        default_css_path = os.path.join(os.path.dirname(__file__), 'styles', 'default.css')
        if os.path.exists(default_css_path):
            stylesheets.append(CSS(filename=default_css_path))

        html_doc.write_pdf(self.output_file, stylesheets=stylesheets)
        print(f"Successfully converted '{self.input_file}' to '{self.output_file}'")

