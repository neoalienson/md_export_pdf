import os

import logging
logger = logging.getLogger(__name__)

def get_stylesheets(css_file, header_css, footer_css, cover_css):
    logger.debug("Getting stylesheets.")
    stylesheets = []

    if css_file and os.path.exists(css_file):
        logger.debug(f"Adding main CSS file: {css_file}")
        with open(css_file, "r", encoding="utf-8") as f:
            stylesheets.append(f.read())
    else:
        logger.warning(f"Main CSS file not found: {css_file}")

    if header_css and os.path.exists(header_css):
        logger.debug(f"Adding header CSS file: {header_css}")
        with open(header_css, "r", encoding="utf-8") as f:
            stylesheets.append(f.read())
    else:
        logger.warning(f"Header CSS file not found: {header_css}")

    if footer_css and os.path.exists(footer_css):
        logger.debug(f"Adding footer CSS file: {footer_css}")
        with open(footer_css, "r", encoding="utf-8") as f:
            stylesheets.append(f.read())
    else:
        logger.warning(f"Footer CSS file not found: {footer_css}")

    if cover_css and os.path.exists(cover_css):
        logger.debug(f"Adding cover CSS file: {cover_css}")
        with open(cover_css, "r", encoding="utf-8") as f:
            stylesheets.append(f.read())
    else:
        logger.warning(f"Cover CSS file not found: {cover_css}")

    return stylesheets
