import os
import markdown
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)
from .config import MARKDOWN_PREPROCESSOR_PIPELINE
from .md_preprocessor.front_matter import FrontMatterProcessor


def convert_markdown_to_html(md_content):
    logger.info("Starting Markdown to HTML conversion.")

    current_md_content = md_content
    front_matter_data = {}

    # Sort processors by priority
    sorted_processors = sorted(MARKDOWN_PREPROCESSOR_PIPELINE, key=lambda p: p.priority)

    for processor_instance in sorted_processors:
        processed_content, extracted_data = processor_instance.process_markdown(current_md_content)
        current_md_content = processed_content
        front_matter_data.update(extracted_data)
        logger.debug(
            f"Applied Markdown pre-processor: {processor_instance.__class__.__name__}"
        )

    logger.debug("Performing basic Markdown to HTML conversion.")
    md = markdown.Markdown(
        extensions=["extra", "codehilite", "toc", "attr_list", "tables", "markdown_sub_sup"],
        extension_configs={"toc": {"toc_depth": 4, "anchorlink": False}},
    )
    html = md.convert(current_md_content)
    logger.debug("Basic Markdown to HTML conversion complete.")

    # Re-parse HTML after prepending TOC to ensure BeautifulSoup sees the complete structure
    soup = BeautifulSoup(html, "html.parser")

    logger.info("Markdown to HTML conversion completed.")
    logger.debug(
        f"Returning: html_content_type={type(str(soup))}, front_matter_data_type={type(front_matter_data)}"
    )
    return str(soup), front_matter_data
