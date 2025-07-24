# run_no_header.py

import os
import logging
from markdown_to_pdf.core import MarkdownToPdfConverter

# Configure logging to show DEBUG messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get the logger for the markdown_to_pdf package and set its level to DEBUG
import markdown_to_pdf
markdown_to_pdf.logger.setLevel(logging.DEBUG)

# Define file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
input_md_file = os.path.join(current_dir, "example.md")

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

# --- Conversion without Header ---
output_pdf_file_no_header = os.path.join(current_dir, "example_no_header.pdf")
print(f"Converting '{input_md_file}' to '{output_pdf_file_no_header}' (without header)...")
try:
    converter_no_header = MarkdownToPdfConverter(
        input_file=input_md_file,
        output_file=output_pdf_file_no_header,
        css_file=css_file,
        header_file=None, # Explicitly set to None for no header
        header_css=header_css_file,
        footer_file=footer_file,
        footer_css=footer_css_file,
        cover_page_file=cover_page_file
    )
    converter_no_header.convert()
    print("Conversion without header complete!")
    print(f"You can find the generated PDF at: {output_pdf_file_no_header}")
except Exception as e:
    print(f"An error occurred during conversion without header: {e}")
