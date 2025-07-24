import markdown
from bs4 import BeautifulSoup
import re
from . import utils
from . import logger

def convert_markdown_to_html(md_content):
    logger.info("Starting Markdown to HTML conversion.")
    # Convert Mermaid.js blocks to image placeholders before general Markdown conversion
    logger.debug("Starting Mermaid.js block conversion.")
    def replace_mermaid_block(match):
        mermaid_code = match.group(1)
        logger.debug(f"Found Mermaid block:\n{mermaid_code}")
        try:
            image_path = utils.convert_mermaid_to_image(mermaid_code)
            logger.info(f"Successfully converted Mermaid block to image: {image_path}")
            return f'<p><img src="{image_path}" alt="Mermaid Diagram"></p>'
        except Exception as e:
            logger.error(f"Error converting Mermaid diagram: {e}", exc_info=True)
            return f'<pre><code>{mermaid_code}</code></pre>' # Fallback to code block on error

    # Regex to find fenced code blocks for mermaid
    md_content = re.sub(r'''```mermaid\n(.*?)\n```''', replace_mermaid_block, md_content, flags=re.DOTALL)
    logger.debug("Mermaid.js block conversion complete.")

    logger.debug("Performing basic Markdown to HTML conversion.")
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'attr_list', 'tables'])
    html = md.convert(md_content)
    logger.debug("Basic Markdown to HTML conversion complete.")

    # Prepend Table of Contents if generated
    if md.toc:
        logger.debug("Table of Contents generated, prepending to HTML.")
        html = f'<div class="table-of-contents">{md.toc}</div>{html}'

    logger.debug("Starting post-processing for Confluence-like code blocks.")
    soup = BeautifulSoup(html, 'html.parser')

    for pre_tag in soup.find_all('pre'):
        # Check if the pre_tag is part of a codehilite block
        highlight_div = pre_tag.find_parent('div', class_='highlight')
        if highlight_div:
            # The attr_list extension should have already applied attributes.
            # We can now directly check for them on the highlight_div or pre_tag.

            # Handle code block title
            # The attr_list extension adds attributes directly to the HTML element.
            # We need to check if a 'title' attribute was present in the markdown.
            # Markdown with attr_list would render something like:
            # <div class="highlight" title="Hello World Example">...</div>
            title_text = highlight_div.get('title')
            if title_text:
                title_div = soup.new_tag('div', class_='code-title')
                title_div.string = title_text
                title_div.insert_before(highlight_div) # Insert before the highlight div
                logger.debug(f"Added title '{title_text}' to code block.")

            # Handle line numbers
            # The attr_list extension would add a class like 'linenums' if specified.
            if 'linenums' in highlight_div.get('class', []):
                pre_tag['class'] = pre_tag.get('class', []) + ['linenums']
                logger.debug("Added linenums class to code block.")

                # Wrap each line in a span for CSS line numbering
                code_tag = pre_tag.find('code')
                if code_tag and code_tag.string:
                    lines = code_tag.string.splitlines()
                    new_code_content = soup.new_tag('code')
                    for line in lines:
                        line_span = soup.new_tag('span', class_='line')
                        line_span.string = line
                        new_code_content.append(line_span)
                        new_code_content.append(soup.new_tag('br')) # Add line break
                    # Remove the last <br> if it's there
                    if new_code_content.contents and new_code_content.contents[-1].name == 'br':
                        new_code_content.contents.pop()
                    code_tag.replace_with(new_code_content)
                    logger.debug("Wrapped code lines with span for numbering.")
    logger.info("Markdown to HTML conversion completed.")
    return str(soup)
