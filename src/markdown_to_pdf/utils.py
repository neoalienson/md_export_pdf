import os
import markdown
import re
import tempfile
import subprocess

def read_file_content(file_path):
    if not file_path or not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # If it's a markdown file, convert to HTML
    if file_path.lower().endswith(('.md', '.markdown')):
        return markdown.markdown(content)
    return content # Assume HTML or plain text

def convert_mermaid_to_image(mermaid_code):
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
