# tests/test_converter.py

import os
import pytest
from markdown_to_pdf.converter import MarkdownToPdfConverter

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
