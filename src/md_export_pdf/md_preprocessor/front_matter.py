import re
import logging
import yaml
from ..base_processor import MarkdownPreprocessor

logger = logging.getLogger(__name__)

class FrontMatterProcessor(MarkdownPreprocessor):
    def __init__(self, priority: int = 10):
        super().__init__(priority)

    def process(self, md_content: str) -> str:
        processed_content, _ = self.process_markdown(md_content)
        return processed_content

    def process_markdown(self, md_content: str) -> tuple[str, dict]:
        logger.debug("Attempting to remove front matter from Markdown content.")
        front_matter_pattern = re.compile(r"^---\s*\n(.*?)(\n|\r\n)---\s*\n", re.DOTALL)

        match = front_matter_pattern.match(md_content)
        front_matter_data = {}

        if match:
            front_matter_str = match.group(1)
            remaining_content = md_content[match.end() :]
            logger.info(f"Front matter found. Content: {front_matter_str[:50]}...")
            try:
                front_matter_data = yaml.safe_load(front_matter_str)
                if not isinstance(front_matter_data, dict):
                    logger.warning(
                        "Front matter is not a dictionary. Returning empty dict."
                    )
                    front_matter_data = {}
            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML front matter: {e}")
                front_matter_data = {}
            return remaining_content.strip(), front_matter_data
        else:
            logger.debug("No front matter found.")
            return md_content, front_matter_data