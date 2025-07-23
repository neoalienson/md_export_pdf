# tests/test_converter.py

import os
import pytest
from markdown_to_pdf.core import MarkdownToPdfConverter

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
