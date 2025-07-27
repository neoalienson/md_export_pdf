import markdown
from bs4 import BeautifulSoup
import os
import re
import tempfile
import subprocess

def _convert_mermaid_to_image(mermaid_code):
    # Create temporary files for mermaid input and image output
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mmd') as mmd_file:
        mmd_file.write(mermaid_code)
        mmd_path = mmd_file.name

    png_path = mmd_path.replace('.mmd', '.png')

    try:
        # Execute mmdc to convert mermaid to PNG
        command = f"mmdc -i {mmd_path} -o {png_path}"
        # Using subprocess directly as run_shell_command doesn't return stdout/stderr for error handling easily
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        if result.stderr:
            print(f"mmdc stderr: {result.stderr}")
        return png_path
    except subprocess.CalledProcessError as e:
        print(f"Error running mmdc: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        raise
    finally:
        # Clean up temporary .mmd file
        if os.path.exists(mmd_path):
            os.remove(mmd_path)

def convert_markdown_to_html(md_content):
    # Convert Mermaid.js blocks to image placeholders before general Markdown conversion
    def replace_mermaid_block(match):
        mermaid_code = match.group(1).strip()
        try:
            image_path = _convert_mermaid_to_image(mermaid_code)
            return f'<p><img src="{image_path}" alt="Mermaid Diagram"></p>'
        except Exception as e:
            logger.error(f"Error converting Mermaid diagram: {e}")
            return f'<pre><code>{mermaid_code}</code></pre>' # Fallback to code block on error

    # Regex to find fenced code blocks for mermaid
    md_content = re.sub(r'```mermaid\n(.*?)```', replace_mermaid_block, md_content, flags=re.DOTALL)

    # Basic Markdown to HTML conversion with attr_list
    md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'attr_list'])
    html = md.convert(md_content)

    # Prepend Table of Contents if generated
    if md.toc:
        html = f'<div class="table-of-contents"><h1>Table of Content</h1>{md.toc}</div><div class="toc-page-break">{html}</div>'

    # Post-process HTML for Confluence-like code blocks (titles and line numbers)
    soup = BeautifulSoup(html, 'html.parser')

    for pre_tag in soup.find_all('pre'):
        # Check if the pre_tag is part of a codehilite block
        highlight_div = pre_tag.find_parent('div', class_='highlight')
        if highlight_div:
            # Handle code block title
            if 'title' in pre_tag.attrs:
                title_text = pre_tag['title']
                title_div = soup.new_tag('div', class_='code-title')
                title_div.string = title_text
                highlight_div.insert_before(title_div) # Insert before the highlight div
                del pre_tag['title'] # Remove attribute from pre tag

            # Handle line numbers
            if 'linenums' in pre_tag.attrs and pre_tag['linenums'].lower() == 'true':
                pre_tag['class'] = pre_tag.get('class', []) + ['linenums']
                del pre_tag['linenums'] # Remove attribute from pre tag

                # Wrap each line in a span for CSS line numbering
                code_tag = pre_tag.find('code')
                if code_tag and code_tag.string:
                    lines = code_tag.string.splitlines()
                    new_code_content = soup.new_tag('code')
                    for line in lines:
                        line_span = soup.new_tag('span', class_='line')
                        line_span.string = line
                        new_code_content.append(line_span)
                        new_code_content.append(soup.new_tag('br')) # Add line break
                    # Remove the last <br> if it's there
                    if new_code_content.contents and new_code_content.contents[-1].name == 'br':
                        new_code_content.contents.pop()
                    code_tag.replace_with(new_code_content)

    return str(soup)
