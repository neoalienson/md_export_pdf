import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
from markdown_to_pdf.converter import MarkdownToPdfConverter
from weasyprint import HTML, CSS

@patch('weasyprint.HTML')
@patch('weasyprint.CSS')
def test_cover_page_no_header_footer(mock_css, mock_html):
    # Create dummy markdown files
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as cover_md_file:
        cover_md_file.write("# Cover Page Title")
        cover_page_path = cover_md_file.name

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as main_md_file:
        main_md_file.write("# Main Content\nThis is the main content.")
        main_content_path = main_md_file.name

    output_pdf_path = "test_output.pdf"

    converter = MarkdownToPdfConverter(
        input_file=main_content_path,
        output_file=output_pdf_path,
        cover_page_file=cover_page_path
    )

    converter.convert()

    # Assert that HTML and CSS were called
    mock_html.assert_called_once()
    mock_css.assert_called() # Should be called multiple times for default and cover CSS

    # Check the CSS passed to WeasyPrint
    # We need to find the CSS string that contains the @page :first rule
    found_cover_css_rule = False
    for call_arg in mock_css.call_args_list:
        if 'string' in call_arg.kwargs:
            css_string = call_arg.kwargs['string']
            if "@page :first" in css_string and "@top-center { content: none; }" in css_string and "@bottom-center { content: none; }" in css_string:
                found_cover_css_rule = True
                break
    assert found_cover_css_rule, "CSS for cover page header/footer suppression not found."

    # Clean up dummy files
    os.remove(cover_page_path)
    os.remove(main_content_path)
    if os.path.exists(output_pdf_path):
        os.remove(output_pdf_path)
