import re
import logging
logger = logging.getLogger(__name__)

def remove_front_matter(md_content: str) -> str:
    """
    Removes YAML front matter from Markdown content.
    Front matter is typically enclosed by '---' at the beginning and end of the block.
    """
    logger.debug("Attempting to remove front matter from Markdown content.")
    # Regex to find front matter: starts with '---' at the beginning of the string,
    # followed by any characters (non-greedy), and ends with '---' on a new line.
    front_matter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

    match = front_matter_pattern.match(md_content)
    if match:
        front_matter_content = match.group(1)
        remaining_content = md_content[match.end():]
        logger.info(f"Front matter found and removed. Content: {front_matter_content[:50]}...")
        return remaining_content.strip()
    else:
        logger.debug("No front matter found.")
        return md_content
