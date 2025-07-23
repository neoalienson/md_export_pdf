from markdown_to_pdf.html_generator import convert_markdown_to_html
import os

# Read the content of the minimal Markdown file
current_dir = os.path.dirname(os.path.abspath(__file__))
md_file_path = os.path.join(current_dir, 'test_code_block.md')

with open(md_file_path, 'r', encoding='utf-8') as f:
    md_content = f.read()

html_output = convert_markdown_to_html(md_content)
print(html_output)
