import logging
import os
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def apply_weasyprint_header_footer(soup: BeautifulSoup, converter_instance):
    # Populate header content if using WeasyPrint for headers
    if not converter_instance.use_pymupdf_header:
        logger.debug("Populating WeasyPrint header content.")
        header_html_content = converter_instance.header_content
        if converter_instance.header_file:
            file_content = converter_instance._read_file_content(
                converter_instance.header_file
            )
            if file_content is not None:
                header_html_content = file_content

        if header_html_content:
            # Create a div for the header content and insert it at the beginning of the body
            header_element = soup.new_tag(
                "div", id="pdf-header", class_="document-header"
            )
            header_element.append(BeautifulSoup(header_html_content, "html.parser"))
            soup.body.insert(
                1, header_element
            )  # Insert after cover page if present, or at beginning
            logger.debug("WeasyPrint header content appended.")

    # Populate footer content with page number placeholders if using WeasyPrint for footers
    if not converter_instance.use_pymupdf_footer:
        logger.debug("Populating WeasyPrint footer content.")
        footer_html_content = converter_instance.footer_content
        if converter_instance.footer_file:
            file_content = converter_instance._read_file_content(
                converter_instance.footer_file
            )
            if file_content is not None:
                footer_html_content = file_content

        if footer_html_content:
            # Replace placeholders for page numbering
            footer_html = footer_html_content.replace(
                "{page_num}", '<span class="page-number"></span>'
            )
            footer_html = footer_html.replace(
                "{total_pages}", '<span class="total-pages"></span>'
            )

            # Create a div for the footer content and append it to the body
            footer_element = soup.new_tag(
                "div", id="pdf-footer", class_="document-footer"
            )
            footer_element.append(BeautifulSoup(footer_html, "html.parser"))
            soup.body.append(footer_element)
            logger.debug("WeasyPrint footer content appended.")

    return soup
