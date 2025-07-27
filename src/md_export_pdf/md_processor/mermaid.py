import re
import logging
logger = logging.getLogger(__name__)
from .. import utils

def process_mermaid_blocks(markdown_content):
    logger.debug("Starting Mermaid.js block conversion in separate processor.")
    
    # Regex to find Mermaid code blocks: ```mermaid ... ```
    # It captures the content within the block.
    mermaid_block_pattern = re.compile(r'```mermaid\n(.*?)```', re.DOTALL)

    def replace_mermaid_block(match):
        mermaid_code = match.group(1)
        logger.debug(f"Found Mermaid block in Markdown:\n{mermaid_code}")
        try:
            image_data_uri = utils.convert_mermaid_to_image(mermaid_code)
            logger.info(f"Successfully converted Mermaid block to image.")
            # Return a Markdown image tag
            return f"![Mermaid Diagram]({image_data_uri})"
        except Exception as e:
            logger.error(f"Error converting Mermaid diagram: {e}", exc_info=True)
            # Fallback to original code block if conversion fails
            return match.group(0) # Keep the original markdown block

    modified_content = mermaid_block_pattern.sub(replace_mermaid_block, markdown_content)
    
    logger.debug("Mermaid.js block conversion complete in separate processor.")
    return modified_content
