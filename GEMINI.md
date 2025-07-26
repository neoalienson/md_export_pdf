# Project Overview

This `markdown-to-pdf` project is a Python tool designed to convert Markdown files into PDF documents. It supports advanced features such as CSS-driven styling, custom headers and footers with page numbering, automatic Table of Contents generation, and conversion of Mermaid.js diagrams into images embedded within the PDF. This tool is specifically designed for **document as code** and **diagram as code** users, aiming for compatibility with document repositories and platforms like Confluence.

## Key Features for Gemini CLI Interaction

- **Markdown to PDF Conversion:** The primary function is to take a Markdown file and produce a PDF.
- **Styling:** Users can provide a CSS file for custom styling.
- **Headers/Footers:** Headers and footers can be specified either directly as content or from a Markdown/HTML file. A key requirement is that these headers and footers must appear on *every* content page of the generated PDF, not just the first or last. They also support independent CSS styling and dynamic page numbering, including placeholders for current page number and total pages (excluding the cover page).
- **Table of Contents:** Automatically generates a clickable Table of Contents.
- **Cover Page:** Supports adding a cover page from a separate Markdown file, which can also be styled via CSS using the `--cover-css` option.
- **Code Blocks:** Supports code syntax highlighting with Confluence-like titles and line numbers.
- **Mermaid.js Support:** The tool automatically renders Mermaid.js code blocks into images. This relies on the `mmdc` (Mermaid CLI) tool being installed and accessible in the system's PATH. You can install it via `npm install -g @mermaid-js/mermaid-cli`.

## Feature Handling Strategies and Requirements

This project implements the following features with specific handling strategies:

- **Markdown to PDF Conversion:** This is the core functionality, handled using PyMuPDF for HTML rendering (Type 1 strategy). This feature has been validated.
- **Mermaid.js Rendering:** Mermaid.js code blocks are rendered into images via the `mmdc` (Mermaid CLI) tool, which is an external tool orchestration (Type 4 strategy). This feature is not yet validated.

These strategies ensure that each feature's interaction and error handling approach aligns with the defined principles.

## Instructions for Gemini CLI

When interacting with this project, consider the following:

- **File Paths:** Always use absolute paths for input Markdown files, output PDF files, and CSS files.
- **Dependencies:** Ensure that all Python dependencies (from `pyproject.toml`) are installed. For Mermaid.js conversion, verify that `mmdc` is installed and accessible in the system's PATH. You can install it via `npm install -g @mermaid-js/mermaid-cli`.
- **Error Handling:** If conversion fails, check for:
    - Missing input files.
    - Invalid CSS file paths.
    - Issues with `mmdc` (e.g., not found, rendering errors).
- **Testing:** Use `pytest` to run tests located in the `tests/` directory.

## Markdown to HTML Conversion Analysis and Strategy

The conversion from Markdown to HTML is a multi-stage process, with each step having potential side effects and interdependencies.

### Step-by-Step Conversion Process:

1.  **Markdown Input**: The process begins with the raw Markdown content provided by the user.

2.  **Pre-processing for Code Block Attributes (`preprocess_markdown_for_code_blocks` in `html_generator.py`)**:
    *   **Purpose**: To extract custom attributes (like `title` and `linenums`) from fenced code blocks that `markdown.Markdown`'s `attr_list` extension might not handle directly when on the same line as the language. It also generates unique IDs for these blocks.
    *   **Mechanism**: Uses regex to find code blocks, parses attributes, stores them in a global dictionary (`_code_block_metadata`), and rewrites the Markdown to place a unique ID (e.g., ````{#unique_id}````) on a new line after the closing fence. This ensures `attr_list` can correctly pick up the ID.
    *   **Potential Side Effects**: This is the most sensitive step. Incorrect regex or Markdown reconstruction can corrupt the Markdown, leading to parsing errors in subsequent steps (e.g., `TypeError` in `fenced_code.py`).

3.  **Basic Markdown to HTML Conversion (using `markdown.Markdown` library in `convert_markdown_to_html`)**:
    *   **Purpose**: To convert the pre-processed Markdown into basic HTML, including syntax highlighting, Table of Contents (TOC) generation, and applying IDs to elements.
    *   **Mechanism**: Initializes `markdown.Markdown` with extensions (`extra`, `codehilite`, `toc`, `attr_list`, `tables`). `codehilite` handles syntax highlighting, `toc` generates the TOC, and `attr_list` applies the unique IDs (from step 2) to the `<pre>` tags. The generated TOC HTML is prepended to the main HTML content.
    *   **Potential Side Effects**: Highly dependent on the output of step 2. Malformed Markdown from pre-processing will cause errors or incorrect HTML. Conflicts between extensions can also arise.

4.  **Post-processing with BeautifulSoup (remaining logic in `convert_markdown_to_html`)**:
    *   **Purpose**: To refine the HTML from `markdown.Markdown` and implement specific features like Mermaid.js diagram conversion, and applying titles and line numbers to code blocks.
    *   **Mechanism**: Parses the HTML using `BeautifulSoup`. It finds Mermaid code blocks, converts them to images, and replaces the original code blocks with `<img>` tags. For other code blocks, it uses the unique IDs (applied in step 3) to retrieve stored `title` and `linenums` metadata and manually inserts title `div`s and wraps code lines in `<span>` tags for line numbering.
    *   **Potential Side Effects**: Relies on correct HTML structure and presence of unique IDs from previous steps. Issues here will result in incorrect rendering of specific features. External dependency on `mmdc` for Mermaid.js conversion can also cause failures.

### Priority of Steps:

The steps are highly interdependent, making proper sequencing and error handling crucial.

1.  **Highest Priority: Step 2 (Pre-processing for Code Block Attributes)**: This is the foundation. Any errors here will propagate and break subsequent steps. Ensuring this step correctly transforms Markdown into a format `markdown.Markdown` can reliably process is paramount.

2.  **Second Highest Priority: Step 3 (Basic Markdown to HTML Conversion)**: Once the Markdown input is guaranteed to be valid, ensuring the core `markdown.Markdown` library and its extensions function as expected is vital for generating a correct base HTML structure.

3.  **Third Priority: Step 4 (Post-processing with BeautifulSoup)**: This step refines the HTML. While important for features, it depends on the successful completion of the previous steps. Issues here are generally easier to isolate and fix once the earlier stages are stable.