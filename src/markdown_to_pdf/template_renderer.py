from bs4 import BeautifulSoup
from . import utils
from . import logger
import markdown

def apply_html_template(html_content, header_content, header_file, footer_content, footer_file, cover_page_file):
    logger.info("Applying HTML template to generate final HTML structure.")
    # Create a basic HTML structure
    # Include dedicated divs for header and footer that are always present
    template_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Markdown to PDF</title>
    </head>
    <body>
        <div id="pdf-header" class="document-header"></div>
        <div class="content">
            {html_content}
        </div>
        <div id="pdf-footer" class="document-footer"></div>
    </body>
    </html>
    """
    soup = BeautifulSoup(template_html, 'html.parser')

    # Insert cover page if provided
    cover_page_html = ""
    if cover_page_file:
        logger.debug(f"Checking for cover page file: {cover_page_file}")
        cover_page_md_content = utils.read_file_content(cover_page_file)
        if cover_page_md_content:
            logger.info(f"Processing cover page from {cover_page_file}")
            cover_page_html = markdown.markdown(cover_page_md_content)
        else:
            logger.warning(f"Cover page file not found or empty: {cover_page_file}")

    if cover_page_html:
        cover_page_div = soup.new_tag("div", id="cover-page")
        cover_page_div.append(BeautifulSoup(cover_page_html, 'html.parser'))
        soup.body.insert(0, cover_page_div)
        logger.info("Cover page successfully added.")

    # Populate header content
    header_html_content = header_content
    if header_file:
        logger.debug(f"Checking for header file: {header_file}")
        file_content = utils.read_file_content(header_file)
        if file_content is not None:
            header_html_content = file_content
        else:
            logger.warning(f"Header file not found or empty: {header_file}")

    if header_html_content:
        logger.info("Adding header content.")
        soup.find(id="pdf-header").append(BeautifulSoup(header_html_content, 'html.parser'))

    # Populate footer content with page number placeholders
    footer_html_content = footer_content
    if footer_file:
        logger.debug(f"Checking for footer file: {footer_file}")
        file_content = utils.read_file_content(footer_file)
        if file_content is not None:
            footer_html_content = file_content
        else:
            logger.warning(f"Footer file not found or empty: {footer_file}")

    if footer_html_content:
        logger.info("Adding footer content.")
        # Replace placeholders for page numbering
        footer_html = footer_html_content.replace('{page_num}', '<span class="page-number"></span>')
        footer_html = footer_html.replace('{total_pages}', '<span class="total-pages"></span>')

        footer_element = soup.find(id="pdf-footer")
        footer_element.append(BeautifulSoup(footer_html, 'html.parser'))

    logger.info("HTML template application complete.")
    return str(soup)
