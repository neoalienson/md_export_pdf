# src/markdown_to_pdf/cli.py

import argparse
import logging
from .core import MarkdownToPdfConverter
from . import logger

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF.")
    parser.add_argument("input_file", help="Path to the input Markdown file.")
    parser.add_argument("-o", "--output", default="output.pdf", help="Path to the output PDF file.")
    parser.add_argument("-s", "--style", help="Path to a CSS file for styling.")
    parser.add_argument("--header", help="Content for the page header.")
    parser.add_argument("--footer", help="Content for the page footer. Use {page_num} and {total_pages} for numbering.")
    parser.add_argument("--cover-page", help="Path to a Markdown file for the cover page.")

    # Header options
    header_group = parser.add_mutually_exclusive_group()
    header_group.add_argument("--header", help="Content for the page header.")
    header_group.add_argument("--header-file", help="Path to a Markdown/HTML file for the page header.")
    parser.add_argument("--header-css", help="Path to a CSS file for header styling.")

    # Footer options
    footer_group = parser.add_mutually_exclusive_group()
    footer_group.add_argument("--footer", help="Content for the page footer. Use {page_num} and {total_pages} for numbering.")
    footer_group.add_argument("--footer-file", help="Path to a Markdown/HTML file for the page footer.")
    parser.add_argument("--footer-css", help="Path to a CSS file for footer styling.")

    parser.add_argument("--cover-page", help="Path to a Markdown file for the cover page.")
    parser.add_argument("--cover-css", help="Path to a CSS file for cover page styling.")

    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level.")

    args = parser.parse_args()

    # Set logging level based on argument
    logger.setLevel(getattr(logging, args.log_level.upper()))

    logger.info(f"Starting Markdown to PDF conversion for '{args.input_file}'")
    try:
        converter = MarkdownToPdfConverter(
            input_file=args.input_file,
            output_file=args.output,
            css_file=args.style,
            header_content=args.header,
            header_file=args.header_file,
            header_css=args.header_css,
            footer_content=args.footer,
            footer_file=args.footer_file,
            footer_css=args.footer_css,
            cover_page_file=args.cover_page,
            cover_css=args.cover_css
        )
        converter.convert()
        logger.info("Markdown to PDF conversion completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during conversion: {e}", exc_info=True)

if __name__ == "__main__":
    main()
