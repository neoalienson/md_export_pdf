import os
import markdown
from bs4 import BeautifulSoup
import re
from . import utils
from . import logger
from . import mermaid_processor

# Dictionary to store metadata for code blocks
_code_block_metadata = {}

def preprocess_markdown_for_code_blocks(md_content):
    global _code_block_metadata
    _code_block_metadata = {} # Clear previous metadata

    # Regex to find fenced code blocks with optional attributes on the first line
    # Captures: (opening_fence), (language), (attributes_string_on_line), (code_content)
    # Example: ```python {title="Hello World" linenums="true"}\ncode\n```
    # Group 1: ```
    # Group 2: python
    # Group 3: {title="Hello World" linenums="true"} or just "title"
    # Group 4: code
    code_block_pattern = re.compile(r'^(```)(\w+)\s*(.*)?\n(.*?)\n^```\s*', re.MULTILINE | re.DOTALL)

    processed_content_parts = []
    last_end = 0
    block_id_counter = 0

    for match in code_block_pattern.finditer(md_content):
        start, end = match.span()
        processed_content_parts.append(md_content[last_end:start])

        opening_fence = match.group(1) # e.g., ```
        lang = match.group(2).strip() # e.g., python
        attributes_str_on_line = match.group(3).strip() # e.g., {title="Hello World" linenums="true"} or just "title"
        code_content = match.group(4)

        title = None
        linenums = False

        # Parse attributes_str_on_line for title and linenums
        if attributes_str_on_line:
            # Check if attributes are in curly braces
            if attributes_str_on_line.startswith('{') and attributes_str_on_line.endswith('}'):
                clean_attributes_str = attributes_str_on_line.strip('{}').strip()
            else:
                clean_attributes_str = attributes_str_on_line # Assume it's just a word like 'title' or 'linenums'

            # Extract title
            title_match = re.search(r'title="([^"]*)"|\'title\'', clean_attributes_str)
            if title_match:
                title = title_match.group(1) if title_match.group(1) else title_match.group(0)

            # Extract linenums
            if 'linenums' in clean_attributes_str:
                linenums = True

        current_block_id = f"code_block_{block_id_counter}"
        _code_block_metadata[current_block_id] = {
            "lang": lang,
            "title": title,
            "linenums": linenums
        }

        # Reconstruct the fenced code block for markdown.Markdown
        # Only include the language in the opening fence.
        # Place the unique ID on a new line immediately after the closing fence for attr_list.
        processed_content_parts.append(f"{opening_fence}{lang}\n{code_content}\n```\n{{#{current_block_id}}}\n")
        block_id_counter += 1
        last_end = end

    processed_content_parts.append(md_content[last_end:])
    return "".join(processed_content_parts)


def convert_markdown_to_html(md_content):
    logger.info("Starting Markdown to HTML conversion.")

    md_content = mermaid_processor.process_mermaid_blocks(md_content)

    # Pre-process markdown to handle custom code block attributes
    preprocessed_md_content = preprocess_markdown_for_code_blocks(md_content)
    logger.debug("Markdown pre-processed for code block attributes.")

    logger.debug("Performing basic Markdown to HTML conversion.")
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'attr_list', 'tables'], extension_configs={'toc': {'toc_depth': 3, 'anchorlink': True}})
    html = md.convert(preprocessed_md_content)
    logger.debug("Basic Markdown to HTML conversion complete.")

    # Get the TOC HTML
    toc_html = md.toc
    if toc_html:
        logger.debug("TOC HTML generated. Prepending to main content.")
        html = toc_html + html

    # Re-parse HTML after prepending TOC to ensure BeautifulSoup sees the complete structure
    soup = BeautifulSoup(html, 'html.parser')

    logger.info("Markdown to HTML conversion completed.")
    return str(soup)
