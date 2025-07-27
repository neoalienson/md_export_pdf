import os
import logging

logger = logging.getLogger(__name__)

def write_html_for_debug(html_content: str, output_file_path: str):
    debug_html_path = output_file_path.replace(".pdf", ".debug.html")
    try:
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Debug HTML saved to: {debug_html_path}")
    except Exception as e:
        logger.error(f"Error saving debug HTML to {debug_html_path}: {e}")
