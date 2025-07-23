import pytest
from unittest.mock import patch, MagicMock
import os
import subprocess
from markdown_to_pdf.markdown_processor import convert_markdown_to_html, _convert_mermaid_to_image

# Mock subprocess.run for _convert_mermaid_to_image
@patch('subprocess.run')
def test_convert_mermaid_to_image_success(mock_run):
    mock_run.return_value = MagicMock(stderr='', returncode=0)
    mermaid_code = "graph TD; A-->B;"
    image_path = _convert_mermaid_to_image(mermaid_code)
    assert image_path.endswith('.png')
    mock_run.assert_called_once()
    # Clean up the created dummy file
    if os.path.exists(image_path):
        os.remove(image_path)

@patch('subprocess.run')
def test_convert_mermaid_to_image_failure(mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd', stderr='Error')
    mermaid_code = "graph TD; A-->B;"
    with pytest.raises(subprocess.CalledProcessError):
        _convert_mermaid_to_image(mermaid_code)

# Test convert_markdown_to_html
def test_convert_markdown_to_html_basic_markdown():
    md_content = "# Hello World\n\nThis is **bold** text."
    html = convert_markdown_to_html(md_content)
    assert "<h1>Hello World</h1>" in html
    assert "This is <strong>bold</strong> text." in html

@patch('markdown_to_pdf.markdown_processor._convert_mermaid_to_image', return_value='/tmp/test_mermaid.png')
def test_convert_markdown_to_html_with_mermaid(mock_convert_mermaid):
    md_content = "```mermaid\ngraph TD; A-->B;\n```"
    html = convert_markdown_to_html(md_content)
    assert '<p><img src="/tmp/test_mermaid.png" alt="Mermaid Diagram"></p>' in html
    mock_convert_mermaid.assert_called_once_with("graph TD; A-->B;")

def test_convert_markdown_to_html_with_toc():
    md_content = "# Title 1\n## Subtitle 1\n# Title 2"
    html = convert_markdown_to_html(md_content)
    assert '<div class="table-of-contents">' in html
    assert '<a href="#title-1">Title 1</a>' in html
    assert '<a href="#subtitle-1">Subtitle 1</a>' in html

def test_convert_markdown_to_html_code_block_with_title():
    md_content = "```python {title=\"My Code\"}\nprint('Hello')\n```"
    html = convert_markdown_to_html(md_content)
    assert '<div class="code-title">My Code</div>' in html
    assert '''<pre><code class="language-python">print('Hello')\n</code></pre>''' in html

def test_convert_markdown_to_html_code_block_with_linenums():
    md_content = "```python {linenums=\"true\"}\nline1\nline2\n```"
    html = convert_markdown_to_html(md_content)
    assert '<pre><code class="language-python linenums">' in html
    assert '<span class="line">line1</span>' in html
    assert '<span class="line">line2</span>' in html
    assert '<br/>' in html

def test_convert_markdown_to_html_code_block_with_title_and_linenums():
    md_content = "```python {title=\"My Code\" linenums=\"true\"}\nline1\nline2\n```"
    html = convert_markdown_to_html(md_content)
    assert '<div class="code-title">My Code</div>' in html
    assert '<pre><code class="language-python linenums">' in html
    assert '<span class="line">line1</span>' in html
    assert '<span class="line">line2</span>' in html


