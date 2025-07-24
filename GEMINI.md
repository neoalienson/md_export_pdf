# Project Overview

This `markdown-to-pdf` project is a Python tool designed to convert Markdown files into PDF documents. It supports advanced features such as CSS-driven styling, custom headers and footers with page numbering, automatic Table of Contents generation, and conversion of Mermaid.js diagrams into images embedded within the PDF. This tool is specifically designed for **document as code** and **diagram as code** users, aiming for compatibility with document repositories and platforms like Confluence.

## Key Features for Gemini CLI Interaction

- **Markdown to PDF Conversion:** The primary function is to take a Markdown file and produce a PDF.
- **Styling:** Users can provide a CSS file for custom styling.
- **Headers/Footers:** Headers and footers can be specified either directly as content or from a Markdown/HTML file. A key requirement is that these headers and footers must appear on *every* content page of the generated PDF, not just the first or last. They also support independent CSS styling and dynamic page numbering, including placeholders for current page number and total pages.
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
