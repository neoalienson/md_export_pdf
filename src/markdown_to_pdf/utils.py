import os
import markdown
import re
import tempfile
import subprocess
from . import logger

def read_file_content(file_path):
    logger.debug(f"Attempting to read file: {file_path}")
    if not file_path or not os.path.exists(file_path):
        logger.warning(f"File not found or path is empty: {file_path}")
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # If it's a markdown file, convert to HTML
    if file_path.lower().endswith(('.md', '.markdown')):
        logger.debug(f"Converting markdown file to HTML: {file_path}")
        return markdown.markdown(content)
    logger.debug(f"Read file content (assuming HTML or plain text): {file_path}")
    return content # Assume HTML or plain text

def convert_mermaid_to_image(mermaid_code):
    logger.debug("Converting Mermaid code to image.")
    # Create temporary files for mermaid input and image output
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mmd') as mmd_file:
        mmd_file.write(mermaid_code)
        mmd_path = mmd_file.name
    logger.debug(f"Temporary Mermaid input file created: {mmd_path}")

    png_path = mmd_path.replace('.mmd', '.png')
    logger.debug(f"Temporary PNG output path: {png_path}")

    try:
        # Execute mmdc to convert mermaid to PNG
        command = f"mmdc -i {mmd_path} -o {png_path}"
        logger.info(f"Executing mmdc command: {command}")
        # Using subprocess directly as run_shell_command doesn't return stdout/stderr for error handling easily
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        if result.stderr:
            logger.warning(f"mmdc stderr: {result.stderr}")
        logger.info(f"Mermaid conversion successful. Image saved to: {png_path}")
        return png_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running mmdc: {e}", exc_info=True)
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise
    finally:
        # Clean up temporary .mmd file
        if os.path.exists(mmd_path):
            os.remove(mmd_path)
            logger.debug(f"Cleaned up temporary Mermaid input file: {mmd_path}")
