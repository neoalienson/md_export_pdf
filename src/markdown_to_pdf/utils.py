import os
import markdown
import re
import tempfile
import subprocess
import shutil
from . import logger

def read_file_content(file_path):
    logger.debug(f"Attempting to read file: {file_path}")
    if not file_path:
        logger.warning("File path is empty.")
        return None
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content
        logger.info(f"Read file content (assuming HTML or plain text): {file_path}")
        return content # Assume HTML or plain text
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
        return None

def convert_mermaid_to_image(mermaid_code):
    logger.info("Starting Mermaid code to image conversion.")
    # Create temporary files for mermaid input and image output
    mmd_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mmd') as mmd_file:
            mmd_file.write(mermaid_code)
            mmd_path = mmd_file.name
        logger.debug(f"Temporary Mermaid input file created: {mmd_path}")

        png_path = mmd_path.replace('.mmd', '.png')
        logger.debug(f"Temporary PNG output path: {png_path}")

        # Check if mmdc is available
        if not shutil.which("mmdc"):
            logger.error("Mermaid CLI (mmdc) not found. Please install it via 'npm install -g @mermaid-js/mermaid-cli' and ensure it's in your system's PATH.")
            raise FileNotFoundError("Mermaid CLI (mmdc) not found. Please install it via 'npm install -g @mermaid-js/mermaid-cli' and ensure it's in your system's PATH.")

        # Execute mmdc to convert mermaid to PNG
        command = f"mmdc -i {mmd_path} -o {png_path}"
        logger.info(f"Executing mmdc command: {command}")
        logger.debug(f"Current working directory for mmdc: {os.getcwd()}")
        # Using subprocess directly as run_shell_command doesn't return stdout/stderr for error handling easily
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True, cwd=os.path.dirname(mmd_path))
        if result.stderr:
            logger.warning(f"mmdc stderr: {result.stderr}")
        logger.info(f"Mermaid conversion successful. Image saved to: {png_path}")
        return png_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running mmdc: {e}", exc_info=True)
        logger.error(f"Stdout: {e.stdout}")
        logger.error(f"Stderr: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Mermaid conversion: {e}", exc_info=True)
        raise
    finally:
        # Clean up temporary .mmd file
        if mmd_path and os.path.exists(mmd_path):
            os.remove(mmd_path)
            logger.debug(f"Cleaned up temporary Mermaid input file: {mmd_path}")
