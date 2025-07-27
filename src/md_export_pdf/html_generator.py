import os
import markdown
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)
from .md_processor import mermaid
from .md_processor import front_matter
from .md_processor.code_block_processor import preprocess_markdown_for_code_blocks

def convert_markdown_to_html(md_content):
    logger.info("Starting Markdown to HTML conversion.")

    md_content, front_matter_data = front_matter.remove_front_matter(md_content)
    md_content = mermaid.process_mermaid_blocks(md_content)

    # Pre-process markdown to handle custom code block attributes
    preprocessed_md_content = preprocess_markdown_for_code_blocks(md_content)
    logger.debug("Markdown pre-processed for code block attributes.")

    logger.debug("Performing basic Markdown to HTML conversion.")
    md = markdown.Markdown(
        extensions=["extra", "codehilite", "toc", "attr_list", "tables"],
        extension_configs={"toc": {"toc_depth": 4, "anchorlink": False}},
    )
    html = md.convert(preprocessed_md_content)
    logger.debug("Basic Markdown to HTML conversion complete.")

    # Re-parse HTML after prepending TOC to ensure BeautifulSoup sees the complete structure
    soup = BeautifulSoup(html, "html.parser")

    extracted_links = _extract_links_from_html(soup)

    logger.info("Markdown to HTML conversion completed.")
    logger.debug(
        f"Returning: html_content_type={type(str(soup))}, extracted_links_type={type(extracted_links)}, front_matter_data_type={type(front_matter_data)}"
    )
    logger.debug(
        f"Returning: html_content_len={len(str(soup)) if isinstance(str(soup), str) else 'N/A'}, extracted_links_len={len(extracted_links) if isinstance(extracted_links, list) else 'N/A'}, front_matter_data_len={len(front_matter_data) if isinstance(front_matter_data, dict) else 'N/A'}"
    )
    return str(soup), extracted_links, front_matter_data


def _extract_links_from_html(soup):
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        text = a_tag.get_text()
        links.append({"href": href, "text": text})
    return links
