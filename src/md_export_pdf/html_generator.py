import os
import markdown
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)
from .md_preprocessor import mermaid
from .md_preprocessor import front_matter
from .md_preprocessor.code_block_processor import preprocess_markdown_for_code_blocks

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

    logger.info("Markdown to HTML conversion completed.")
    logger.debug(
        f"Returning: html_content_type={type(str(soup))}, front_matter_data_type={type(front_matter_data)}"
    )
    return str(soup), front_matter_data