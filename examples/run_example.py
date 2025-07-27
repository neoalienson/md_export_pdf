import os
import logging
import md_export_pdf
import argparse
import logging
import sys
from contextlib import contextmanager
from md_export_pdf.converter import MarkdownToPdfConverter
from md_export_pdf.logging_config import configure_third_party_logging

@contextmanager
def suppress_stdout_stderr():
    """A context manager to suppress stdout and stderr."""
    with open(os.devnull, 'w') as fnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = fnull
        sys.stderr = fnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF with various options.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Set the logging level.")
    args = parser.parse_args()

    # Set logging level based on argument
    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {args.log_level}")

    # Configure basic logging for the root logger, forcing re-configuration if necessary
    logging.basicConfig(level=numeric_level, format='%(levelname)s: %(message)s', force=True)

    # Define a logger for this specific script
    logger = logging.getLogger(__name__)

    # Ensure warnings are captured by the logging system (optional, can be removed if still too noisy)
    logging.captureWarnings(True)

    # Configure third-party logging
    configure_third_party_logging()

    # Define file paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_md_file = os.path.join(current_dir, "example.md")
    output_pdf_file = os.path.join(current_dir, "example.pdf")

    # Main CSS for content
    css_file = os.path.join(current_dir, "example.css")

    # Cover page files
    cover_page_file = os.path.join(current_dir, "cover.md")
    cover_css_file = os.path.join(current_dir, "cover.css") # New: Cover page CSS

    # Header files
    header_file = os.path.join(current_dir, "header.md")
    header_css_file = os.path.join(current_dir, "header.css")

    # Footer files
    footer_file = os.path.join(current_dir, "footer.md")
    footer_css_file = os.path.join(current_dir, "footer.css")

    logger.info(f"Converting '{input_md_file}' to '{output_pdf_file}'...")

    try:
        converter = MarkdownToPdfConverter(
            input_file=input_md_file,
            output_file=output_pdf_file,
            css_file=css_file,
            # Use header/footer files and their CSS
            header_file=None,
            header_css=None,
            footer_file=None,
            footer_css=None,
            # Use cover page file and its CSS
            cover_page_file=cover_page_file,
            # Hardcode PyMuPDF usage for header and footer
            use_pymupdf_header=True,
            use_pymupdf_footer=True,
            header_content="My Hardcoded Header", # Example hardcoded header
            footer_content="Page {page_num} of {total_pages}", # Example hardcoded footer
            use_watermark=True,
        )
        converter.convert()
        logger.info("Conversion complete!")
        logger.info(f"You can find the generated PDF at: {output_pdf_file}")
    except Exception as e:
        logger.error(f"An error occurred during conversion: {e}")

if __name__ == "__main__":
    main()