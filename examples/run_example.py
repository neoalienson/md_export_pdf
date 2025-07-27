import os
from markdown_to_pdf.converter import MarkdownToPdfConverter

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

print(f"Converting '{input_md_file}' to '{output_pdf_file}'...")

try:
    converter = MarkdownToPdfConverter(
        input_file=input_md_file,
        output_file=output_pdf_file,
        css_file=css_file,
        # Use header/footer files and their CSS
        header_file=header_file,
        header_css=header_css_file,
        footer_file=footer_file,
        footer_css=footer_css_file,
        # Use cover page file and its CSS
        cover_page_file=cover_page_file,
        # Hardcode PyMuPDF usage for header and footer
        use_pymupdf_header=True,
        use_pymupdf_footer=True,
        header_content="My Hardcoded Header", # Example hardcoded header
        footer_content="Page {page_num} of {total_pages}" # Example hardcoded footer
    )
    converter.convert()
    print("Conversion complete!")
    print(f"You can find the generated PDF at: {output_pdf_file}")
except Exception as e:
    print(f"An error occurred during conversion: {e}")