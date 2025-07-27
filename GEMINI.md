# Project Overview

This `markdown-to-pdf` project is a Python tool designed to convert Markdown files into PDF documents. It supports advanced features such as CSS-driven styling, custom headers and footers with page numbering, automatic Table of Contents generation, and conversion of Mermaid.js diagrams into images embedded within the PDF. This tool is specifically designed for **document as code** and **diagram as code** users, aiming for compatibility with document repositories and platforms like Confluence.

## Default Styling

The default CSS styling for the PDF output is now located in `src/md_export_pdf/styles/default.css`. This file contains base styles for elements, page numbering, and specific adjustments for code blocks and the Table of Contents.

## Key Features for Gemini CLI Interaction

- **Markdown to PDF Conversion:** The primary function is to take a Markdown file and produce a PDF.
- **Styling:** Users can provide a CSS file for custom styling.
- **Headers/Footers:** Headers and footers can be specified either directly as content or from a Markdown/HTML file. This project employs a hybrid approach for header and footer generation: WeasyPrint is used by default for the base PDF conversion due to its superior handling of HTML/CSS rendering and link conversion. However, for consistent header and footer placement across all pages, especially when dealing with complex content or specific rendering quirks, PyMuPDF is utilized as a post-processing step. Options `--use-pymupdf-header` and `--use-pymupdf-footer` are available to switch to PyMuPDF for header and/or footer generation respectively, which might offer more consistent results in some environments. **Note:** When using PyMuPDF for headers/footers, only plain text content is supported; Markdown formatting will not be rendered.
- **Table of Contents:** Automatically generates a clickable Table of Contents with indentation per header level, placed on an independent page.
- **Cover Page:** Supports adding a cover page from a separate Markdown file, which can also be styled via CSS using the `--cover-css` option.
- **Code Blocks:** Supports code syntax highlighting with Confluence-like titles and line numbers.
- **Mermaid.js Support:** The tool automatically renders Mermaid.js code blocks into images. This relies on the `mmdc` (Mermaid CLI) tool being installed and accessible in the system's PATH. You can install it via `npm install -g @mermaid-js/mermaid-cli`.

## Pluggable PDF Post-processing

This project implements a pluggable system for PDF post-processing, allowing for flexible modifications to the generated PDF after the initial conversion by WeasyPrint. This system is built around the `PdfPostProcessor` abstract base class, which defines a standard interface for applying modifications.

-   **`PyMuPdfPostProcessor`**: This is a concrete implementation that leverages PyMuPDF for tasks like adding headers and footers. It is used when `--use-pymupdf-header` or `--use-pymupdf-footer` options are enabled.
-   **`DummyPostProcessor`**: A simple implementation for testing and validation purposes. It performs no actual modifications but logs its execution. It can be enabled using the `--use-dummy-postprocessor` CLI option.

This modular design allows for easy integration of new PDF manipulation functionalities or alternative libraries in the future.

## API Handling Strategies and Error Handling Table

| Tool Name                       | API Handling Strategy Type                          | Validated |
|---------------------------------|----------------------------------------------------|-----------|
| markdown-to-pdf conversion      | N/A (Local file processing, not external API)      | No        |
| Mermaid.js rendering (via mmdc) | Type 4 (External tool orchestration)               | No        |

This table serves as a reference for current and future development, ensuring that each tool's interaction and error handling approach is aligned with the defined principles.

## Instructions for Gemini CLI

When interacting with this project, consider the following:

- **File Paths:** Always use absolute paths for input Markdown files, output PDF files, and CSS files.
- **Dependencies:** Ensure that all Python dependencies (from `pyproject.toml`) are installed. For Mermaid.js conversion, verify that `mmdc` is installed and accessible in the system's PATH. You can install it via `npm install -g @mermaid-js/mermaid-cli`.
- **Error Handling:** If conversion fails, check for:
    - Missing input files.
    - Invalid CSS file paths.
    - Issues with `mmdc` (e.g., not found, rendering errors).
    - **WeasyPrint Dependencies (Windows):** If you encounter an `OSError` related to `libgobject-2.0-0` or other missing libraries, you may need to install GTK3 on your system. Refer to the WeasyPrint installation documentation for details: `https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation`
- **Testing:** Use `pytest` to run tests located in the `tests/` directory.
