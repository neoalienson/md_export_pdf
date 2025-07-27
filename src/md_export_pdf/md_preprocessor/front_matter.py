import re
import logging
import yaml

logger = logging.getLogger(__name__)


def extract_front_matter(md_content: str) -> tuple[str, dict]:
    """
    Removes YAML front matter from Markdown content and returns the content
    and a dictionary of the parsed front matter.
    Front matter is typically enclosed by '---' at the beginning and end of the block.
    """
    logger.debug("Attempting to remove front matter from Markdown content.")
    # Regex to find front matter: starts with '---' at the beginning of the string,
    # followed by any characters (non-greedy), and ends with '---' on a new line.
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
