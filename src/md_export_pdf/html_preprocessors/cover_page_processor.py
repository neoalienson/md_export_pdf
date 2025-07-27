import logging
import os
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def _convert_cover_page_to_html(converter_instance):
    if not converter_instance.cover_page_file or not os.path.exists(
        converter_instance.cover_page_file
    ):
        return ""
    with open(converter_instance.cover_page_file, "r", encoding="utf-8") as f:
        md_content = f.read()
    # Simple Markdown conversion for cover page, no TOC or Mermaid processing
    return markdown.markdown(md_content)


def apply_cover_page(soup: BeautifulSoup, converter_instance):
    cover_page_html = _convert_cover_page_to_html(converter_instance)
    if cover_page_html:
        logger.debug("Cover page HTML generated. Inserting into soup.")
        cover_page_div = soup.new_tag("div", id="cover-page", class_="cover-page")
        cover_page_div.append(BeautifulSoup(cover_page_html, "html.parser"))
        soup.body.insert(0, cover_page_div)
    return soup
