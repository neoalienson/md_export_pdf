import pytest
from unittest.mock import patch, MagicMock
import os
import subprocess
from bs4 import BeautifulSoup
from md_export_pdf.md_processor.markdown import convert_markdown_to_html
from md_export_pdf.converter import MarkdownToPdfConverter
from weasyprint import HTML, CSS

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
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.find('h1', string='Hello World') is not None
    assert soup.find('strong', string='bold') is not None

@patch('md_export_pdf.md_processor.mermaid.convert_mermaid_to_image', return_value='/tmp/test_mermaid.png')
def test_convert_markdown_to_html_with_mermaid(mock_convert_mermaid):
    md_content = "```mermaid\ngraph TD; A-->B;\n```"
    html = convert_markdown_to_html(md_content)
    soup = BeautifulSoup(html, 'html.parser')
    img_tag = soup.find('img')
    assert img_tag is not None
    assert img_tag.get('src') == '/tmp/test_mermaid.png'
    assert img_tag.get('alt') == 'Mermaid Diagram'
    mock_convert_mermaid.assert_called_once_with("graph TD; A-->B;")

def test_convert_markdown_to_html_with_toc():
    md_content = "# Title 1\n## Subtitle 1\n# Title 2"
    html = convert_markdown_to_html(md_content)
    assert '<div class="table-of-contents">' in html
    assert '<div class="toc">' in html
    assert '<a href="#title-1">Title 1</a>' in html
    assert '<a href="#subtitle-1">Subtitle 1</a>' in html

def test_convert_markdown_to_html_code_block():
    md_content = "```python\nprint(\'Hello\')\n```"
    html = convert_markdown_to_html(md_content)
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='codehilite')
    assert div
    pre_tag = soup.find('pre')
    assert pre_tag and 'language-python' in pre_tag.find('code').get('class', [])
    assert 'print(\'Hello\')' in pre_tag.get_text()

# def test_convert_markdown_to_html_code_block_with_title():
#     md_content = "```python {title=\"My Code\"}\nprint(\'Hello\')\n```"
#     html = convert_markdown_to_html(md_content)
#     soup = BeautifulSoup(html, 'html.parser')
#     title_div = soup.find('div', class_='code-title')
#     assert title_div and title_div.get_text() == 'My Code'
#     pre_tag = soup.find('pre')
#     assert pre_tag and 'language-python' in pre_tag.find('code').get('class', [])
#     assert 'print(\'Hello\')' in pre_tag.get_text()

# def test_convert_markdown_to_html_code_block_with_linenums():
#     md_content = "```python {linenums=\"true\"}\nline1\nline2\n```"
#     html = convert_markdown_to_html(md_content)
#     soup = BeautifulSoup(html, 'html.parser')
#     pre_tag = soup.find('pre')
#     assert pre_tag and 'language-python' in pre_tag.find('code').get('class', [])
#     assert 'linenums' in pre_tag.get('class', [])
#     assert soup.find('span', class_='line', string='line1')
#     assert soup.find('span', class_='line', string='line2')

# def test_convert_markdown_to_html_code_block_with_title_and_linenums():
#     md_content = "```python {title=\"My Code\" linenums=\"true\"}\nline1\nline2\n```"
#     html = convert_markdown_to_html(md_content)
#     soup = BeautifulSoup(html, 'html.parser')
#     title_div = soup.find('div', class_='code-title')
#     assert title_div and title_div.get_text() == 'My Code'
#     pre_tag = soup.find('pre')
#     assert pre_tag and 'language-python' in pre_tag.find('code').get('class', [])
#     assert 'linenums' in pre_tag.get('class', [])
#     assert soup.find('span', class_='line', string='line1')
#     assert soup.find('span', class_='line', string='line2')


