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

    logger.debug("Adding default CSS.")
    # Add default CSS for basic styling and header/footer positioning
    default_css = """
    body {
        font-family: sans-serif;
        line-height: 1.5;
    }
    /* Basic styling for code highlighting from Pygments */
    .codehilite pre {
        background-color: #f8f8f8;
        padding: 10px;
        border-radius: 5px;
        overflow-x: auto;
    }
    /* PyMuPDF specific for page numbering */
    .page-number::after {
        content: counter(page);
    }
    .total-pages::after {
        content: counter(pages);
    }
    /* Cover page styling */
    #cover-page {
        page-break-after: always;
        text-align: center;
        padding-top: 20%; /* Adjust as needed for vertical centering */
    }
    /* Confluence-like code block styling */
    .code-title {
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        border-bottom: none;
        padding: 5px 10px;
        font-weight: bold;
        font-size: 0.9em;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
    }
    .codehilite pre {
        margin-top: 0; /* Remove top margin if title is present */
        border-top-left-radius: 0;
        border-top-right-radius: 0;
    }
    .linenums {
        counter-reset: line;
    }
    .linenums .line::before {
        counter-increment: line;
        content: counter(line);
        display: inline-block;
        width: 2em; /* Adjust width as needed */
        padding-right: 10px;
        text-align: right;
        color: #999;
        -webkit-user-select: none;
        user-select: none;
    }
    /* Table of Contents styling for page numbers */
    .table-of-contents ul {
        list-style: none;
        padding-left: 0;
    }
    .table-of-contents li {
        margin-bottom: 0.2em;
    }
    .table-of-contents a {
        display: flex; /* Make the link itself a flex container */
        justify-content: space-between; /* Space out the text and page number */
        align-items: baseline;
        text-decoration: none;
        color: inherit;
    }
    .table-of-contents a::after {
        content: target-counter(attr(href), page); /* Simplified attr(href) */
        margin-left: 1em;
        color: #666;
        font-size: 0.9em;
        white-space: nowrap; /* Prevent page number from wrapping */
    }
    """
    stylesheets.append(default_css)
    return stylesheets
