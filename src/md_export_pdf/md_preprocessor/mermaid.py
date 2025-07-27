import re
import logging
from .. import utils
from ..base_processor import MarkdownPreprocessor

logger = logging.getLogger(__name__)


class MermaidProcessor(MarkdownPreprocessor):
    def __init__(self, priority: int = 20):
        super().__init__(priority)

    def process(self, markdown_content: str) -> str:
        return self.process_markdown(markdown_content)

    def process_markdown(self, markdown_content: str) -> tuple[str, dict]:
        logger.debug("Starting Mermaid.js block conversion in separate processor.")

        mermaid_block_pattern = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)

        def replace_mermaid_block(match):
            mermaid_code = match.group(1)
            logger.debug(f"Found Mermaid block in Markdown:\n{mermaid_code}")
            try:
                image_data_uri = utils.convert_mermaid_to_image(mermaid_code)
                logger.info(f"Successfully converted Mermaid block to image.")
                return f"![Mermaid Diagram]({image_data_uri})"
            except Exception as e:
                logger.error(f"Error converting Mermaid diagram: {e}", exc_info=True)
                return match.group(0)

        modified_content = mermaid_block_pattern.sub(
            replace_mermaid_block, markdown_content
        )

        logger.debug("Mermaid.js block conversion complete in separate processor.")
        return modified_content, {}
