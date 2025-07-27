import pytest
from md_export_pdf.md_processor.mermaid import process_mermaid_blocks
from md_export_pdf import utils


# Mock the convert_mermaid_to_image function to avoid actual image conversion during tests
@pytest.fixture(autouse=True)
def mock_convert_mermaid_to_image(monkeypatch):
    def mock_convert(mermaid_code):
        # For testing, we use a predictable string based on the mermaid_code
        # to ensure consistent expected outputs.
        return f"data:image/png;base64,mocked_image_data_for_{mermaid_code.replace('\n', '_').replace(' ', '')}"

    monkeypatch.setattr(utils, "convert_mermaid_to_image", mock_convert)


def test_mermaid_block_conversion_success():
    markdown_content = """
# My Document

Here is a diagram:

```mermaid
graph TD;
    A-->B;
```

And some more text.
"""

    expected_image_data_uri = (
        "data:image/png;base64,mocked_image_data_for_graphTD;_A-->B;_"
    )
    expected_output = f"""
# My Document

Here is a diagram:

![Mermaid Diagram]({expected_image_data_uri})

And some more text.
"""

    processed_content = process_mermaid_blocks(markdown_content)
    assert processed_content.strip() == expected_output.strip()


def test_mermaid_block_conversion_multiple_blocks():
    markdown_content = """
```mermaid
graph LR;
    A-->B;
```

Some text in between.

```python
some other block in between

```

```mermaid
graph TD;
    C-->D;
```

"""

    expected_image_data_uri_1 = (
        f"data:image/png;base64,mocked_image_data_for_graphLR;_A-->B;_"
    )
    expected_image_data_uri_2 = (
        f"data:image/png;base64,mocked_image_data_for_graphTD;_C-->D;_"
    )

    expected_output = f"""
![Mermaid Diagram]({expected_image_data_uri_1})

Some text in between.

```python
some other block in between

```

![Mermaid Diagram]({expected_image_data_uri_2})
"""

    processed_content = process_mermaid_blocks(markdown_content)
    assert processed_content.strip() == expected_output.strip()


def test_mermaid_block_conversion_no_mermaid():
    markdown_content = """
# My Document

This is a regular markdown file with no mermaid diagrams.

```python
print("Hello")
```
"""

    processed_content = process_mermaid_blocks(markdown_content)
    assert processed_content.strip() == markdown_content.strip()


def test_mermaid_block_conversion_error_fallback(monkeypatch):
    def mock_convert_fail(mermaid_code):
        raise Exception("Mermaid conversion failed")

    monkeypatch.setattr(utils, "convert_mermaid_to_image", mock_convert_fail)

    markdown_content = """
```mermaid
graph TD;
    A-->B;
```
"""

    processed_content = process_mermaid_blocks(markdown_content)
    assert processed_content.strip() == markdown_content.strip()
