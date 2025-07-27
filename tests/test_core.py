# tests/test_converter.py

import os
import pytest
import fitz  # Import fitz for PDF inspection
from md_export_pdf.converter import MarkdownToPdfConverter


@pytest.fixture
def temp_markdown_file(tmp_path):
    content = """
# Test Document

This is a **test** markdown file.

- Item 1
- Item 2

```python
print("Hello, world!")
```

```mermaid
graph TD;
    A-->B;
    B-->C;
    C-->D;
```
"""
    file_path = tmp_path / "test.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def temp_output_pdf(tmp_path):
    return tmp_path / "output.pdf"


def test_converter_instantiation(temp_markdown_file, temp_output_pdf):
    converter = MarkdownToPdfConverter(str(temp_markdown_file), str(temp_output_pdf))
    assert isinstance(converter, MarkdownToPdfConverter)


def test_converter_creates_pdf(temp_markdown_file, temp_output_pdf):
    converter = MarkdownToPdfConverter(str(temp_markdown_file), str(temp_output_pdf))
    converter.convert()
    assert os.path.exists(temp_output_pdf)
    assert os.path.getsize(temp_output_pdf) > 0


def test_end_to_end_conversion_with_table_and_mermaid(tmp_path):
    # Create a markdown file with a table and mermaid diagram
    md_content = """
# Document with Table and Mermaid

## Table Test

| Header 1 | Header 2 |
|----------|----------|
| Data 1   | Data 2   |

## Mermaid Test

```mermaid
graph TD;
    A[Start] --> B[End];
```
"""
    input_md_file = tmp_path / "test_table_mermaid.md"
    input_md_file.write_text(md_content)

    output_pdf_file = tmp_path / "output_table_mermaid.pdf"

    converter = MarkdownToPdfConverter(str(input_md_file), str(output_pdf_file))
    converter.convert()

    assert os.path.exists(output_pdf_file)
    assert os.path.getsize(output_pdf_file) > 0


def test_total_page_logic_with_cover_and_footer(tmp_path):
    # Create dummy content that spans multiple pages
    content_md = (
        """
# Main Content

"""
        + "<p>This is a line of content.</p>\n" * 100
    )  # Enough lines to span multiple pages

    cover_md = """
# Cover Page
"""

    header_md = """
Header Content
"""

    footer_md = """
Page {page_num} of {total_pages}
"""

    input_md_file = tmp_path / "content.md"
    input_md_file.write_text(content_md)

    cover_file = tmp_path / "cover.md"
    cover_file.write_text(cover_md)

    header_file = tmp_path / "header.md"
    header_file.write_text(header_md)

    footer_file = tmp_path / "footer.md"
    footer_file.write_text(footer_md)

    output_pdf_file = tmp_path / "output_with_footer.pdf"

    converter = MarkdownToPdfConverter(
        input_file=str(input_md_file),
        output_file=str(output_pdf_file),
        cover_page_file=str(cover_file),
        header_file=str(header_file),
        footer_file=str(footer_file),
    )
    converter.convert()

    assert os.path.exists(output_pdf_file)
    assert os.path.getsize(output_pdf_file) > 0

    # Open the generated PDF to verify content
    doc = fitz.open(output_pdf_file)

    # The total number of pages in the PDF should be (content pages + 1 for cover)
    # We need to determine the number of content pages dynamically
    # For this test, let's assume at least 2 content pages for the given content
    # and verify the footer on the second page (first content page) and the last content page.

    # Find the actual number of content pages
    # This is a bit tricky without knowing the exact rendering, but we can infer
    # it from the total pages in the document minus the cover page.
    total_pages_in_pdf = doc.page_count
    expected_content_pages = total_pages_in_pdf - 1  # Subtract cover page

    assert expected_content_pages >= 1, "Expected at least one content page."

    # Verify footer on the first content page (index 1, as 0 is cover)
    if total_pages_in_pdf > 1:  # Ensure there's at least one content page
        first_content_page = doc[1]
        # Define the footer area (adjust as per your margin and footer placement)
        # Assuming footer is at the bottom, within the margin area
        footer_rect = fitz.Rect(
            0,
            first_content_page.rect.height - 72,
            first_content_page.rect.width,
            first_content_page.rect.height,
        )
        footer_text = first_content_page.get_text(clip=footer_rect).strip()

        # Assert that the footer contains the correct page number and total pages
        assert f"Page 1 of {expected_content_pages}" in footer_text

    # Verify footer on the last content page
    last_content_page_index = total_pages_in_pdf - 1
    last_content_page = doc[last_content_page_index]
    footer_rect = fitz.Rect(
        0,
        last_content_page.rect.height - 72,
        last_content_page.rect.width,
        last_content_page.rect.height,
    )
    footer_text = last_content_page.get_text(clip=footer_rect).strip()
    assert f"Page {expected_content_pages} of {expected_content_pages}" in footer_text

    doc.close()
