import pytest
from markdown_to_pdf.html_generator import convert_markdown_to_html
import re
import os

# Fixture to read the content of example.md
@pytest.fixture
def example_md_content():
    # Adjust path to be relative to the project root or use an absolute path
    # For testing, it's often better to mock file reads or use a known test file
    # For simplicity, assuming it's accessible relative to where pytest is run
    current_dir = os.path.dirname(os.path.abspath(__file__))
    example_md_path = os.path.join(current_dir, '..', 'examples', 'example.md')
    with open(example_md_path, 'r', encoding='utf-8') as f:
        return f.read()



def test_general_structure_conversion(example_html_soup):
    # Assertions for general structure
    assert example_html_soup.find('h1', string='My Example Document') is not None
    assert example_html_soup.find('h2', string='Features Demonstrated') is not None

def test_table_conversion(example_html_soup):
    # Assertion for table conversion
    table = example_html_soup.find('table')
    assert table is not None, "Table not found in HTML output"
    assert example_html_soup.find('th', string='A') is not None
    assert example_html_soup.find('td', string='3') is not None

def test_code_block_conversion(example_html_soup):
    # Assertion for code block with title and line numbers
    code_title = example_html_soup.find('div', class_='code-title', string='Hello World Example')
    assert code_title is not None, "Code block title not found"
    # Check for line numbers (assuming they are wrapped in spans with class 'line')
    code_block_with_linenums = example_html_soup.find('pre', class_='linenums')
    assert code_block_with_linenums is not None, "Code block with line numbers not found"
    assert code_block_with_linenums.find('span', class_='line') is not None

def test_image_and_link_conversion(example_html_soup):
    # Assertion for image and link
    assert example_html_soup.find('img', src='https://via.placeholder.com/150') is not None
    assert example_html_soup.find('a', href='https://www.google.com', string='Google') is not None