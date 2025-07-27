import os
import fitz
import markdown
from . import utils
from . import html_generator
from . import template_renderer
from . import logger
from . import style_manager

class MarkdownToPdfConverter:
    def __init__(self, input_file, output_file, css_file=None, header_content=None, header_file=None, header_css=None, footer_content=None, footer_file=None, footer_css=None, cover_page_file=None, cover_css=None):
        logger.debug(f"Initializing MarkdownToPdfConverter with input_file={input_file}, output_file={output_file}, css_file={css_file}")
        self.input_file = input_file
        self.output_file = output_file
        self.css_file = css_file
        self.header_content = header_content
        self.header_file = header_file
        self.header_css = header_css
        self.footer_content = footer_content
        self.footer_file = footer_file
        self.footer_css = footer_css
        self.cover_page_file = cover_page_file
        self.cover_css = cover_css

    def convert(self):
        logger.info(f"Starting conversion of '{self.input_file}' to '{self.output_file}'")
        md_content = utils.read_file_content(self.input_file)
        if md_content is None:
            logger.error(f"Input Markdown file not found: {self.input_file}")
            raise FileNotFoundError(f"Input Markdown file not found: {self.input_file}")
        logger.debug(f"Markdown content read from {self.input_file}")
        main_html_content, extracted_links = html_generator.convert_markdown_to_html(md_content)
        logger.debug("Markdown converted to HTML.")

        # Process cover page separately if provided
        cover_page_html = None
        if self.cover_page_file:
            cover_page_md_content = utils.read_file_content(self.cover_page_file)
            if cover_page_md_content:
                md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'attr_list', 'tables'])
                cover_page_html = md.convert(cover_page_md_content)
                logger.info("Cover page HTML generated.")
            else:
                logger.warning(f"Cover page file not found or empty: {self.cover_page_file}")

        # Generate main content HTML
        main_html = template_renderer.apply_html_template(
            html_content=main_html_content,
            header_content=None,
            header_file=None,
            footer_content=None,
            footer_file=None,
            cover_page_file=None  # Cover page handled separately
        )
        logger.debug("Main HTML template applied.")


        # Prepare header HTML
        header_html = ""
        if self.header_content:
            header_html = self.header_content
        elif self.header_file:
            header_md_content = utils.read_file_content(self.header_file)
            if header_md_content:
                md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'attr_list', 'tables'])
                header_html = md.convert(header_md_content)
                logger.info("Header HTML generated.")
            else:
                logger.warning(f"Header file not found or empty: {self.header_file}")

        # Prepare footer HTML
        footer_html = ""
        if self.footer_content:
            footer_html = self.footer_content
        elif self.footer_file:
            footer_md_content = utils.read_file_content(self.footer_file)
            if footer_md_content:
                md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc', 'attr_list', 'tables'])
                footer_html = md.convert(footer_md_content)
                logger.info("Footer HTML generated.")
            else:
                logger.warning(f"Footer file not found or empty: {self.footer_file}")

        # Debug: Save main_html to a temporary file
        debug_html_path = self.output_file.replace(".pdf", ".debug.html")
        with open(debug_html_path, "w", encoding="utf-8") as f:
            f.write(main_html)
        logger.info(f"Debug HTML saved to: {debug_html_path}")

        # Load CSS content
        all_stylesheets = style_manager.get_stylesheets(
            self.css_file,
            self.header_css,
            self.footer_css,
            self.cover_css # Still pass cover_css for general styling if needed
        )
        combined_css_content = ""
        for css_string in all_stylesheets:
            combined_css_content += css_string + "\n"

        import io # Added import for BytesIO

        out_file = io.BytesIO()
        writer = fitz.DocumentWriter(out_file)
        margin = 72  # 1 inch margin (72 points per inch)
        page_rect = fitz.paper_rect("A4") # Assuming A4 paper size for consistency
        content_rect = page_rect + (margin, margin, -margin, -margin) # Apply margins

        # Render cover page if exists
        if cover_page_html:
            cover_story = fitz.Story(html=cover_page_html, user_css=combined_css_content)
            device = writer.begin_page(page_rect)
            cover_story.place(content_rect)
            cover_story.draw(device)
            writer.end_page()
            logger.info("Cover page rendered.")

        # Render main content using fitz.Story for proper pagination
        main_story = fitz.Story(html=main_html, user_css=combined_css_content)
        more = 1
        page_num = 0
        total_pages_content = 0 # Initialize total content pages
        while more:
            page_num += 1
            device = writer.begin_page(page_rect)
            more, _ = main_story.place(content_rect)
            main_story.draw(device)

            # Draw header and footer on each page
            if header_html:
                header_story = fitz.Story(html=header_html, user_css=combined_css_content)
                header_story.place(fitz.Rect(0, 0, page_rect.width, margin))
                header_story.draw(device)

            if footer_html:
                # Replace placeholders for page numbering
                current_footer_html = footer_html.replace('{page_num}', str(page_num))
                # total_pages will be updated after all pages are rendered
                current_footer_html = current_footer_html.replace('{total_pages}', '{total_pages_placeholder}')

                footer_story = fitz.Story(html=current_footer_html, user_css=combined_css_content)
                footer_story.place(fitz.Rect(0, page_rect.height - margin, page_rect.width, page_rect.height))
                footer_story.draw(device)
            writer.end_page()
            logger.info(f"Main content rendered on page {page_num}.")
            total_pages_content = page_num # Update total content pages
        logger.info("All main content rendered across multiple pages using fitz.Story.")

        writer.close() # Close the writer to finalize the PDF in BytesIO

        # Open the BytesIO content as a Document to save it
        doc = fitz.open("pdf", out_file.getvalue())

        # Post-process to update total page numbers in footer
        total_pages_final = doc.page_count
        start_page_offset = 0
        if cover_page_html: # If a cover page exists, it's the first page and not part of content count
            total_pages_final -= 1
            start_page_offset = 1

        # Add clickable links
        for link_info in extracted_links:
            link_text = link_info['text']
            link_href = link_info['href']
            text_instances = doc[1].search_for(link_text)
            for inst in text_instances:
                # Ensure the found text instance is within the content area
                if content_rect.intersects(inst):
                    doc[1].insert_link({"kind": fitz.LINK_URI, "from": inst, "uri": link_href})
                    logger.debug(f"Added link: {link_href} for text: {link_text} at {inst}")            

        for i in range(doc.page_count):
            page = doc[i]
            
            # Skip cover page if it exists and is the current page
            if cover_page_html and i == 0:
                continue

            # Calculate the page number for the footer (1-based for content pages)
            current_content_page_num = i + 1 - start_page_offset

            # Get the footer area (assuming it's at the bottom)
            footer_rect = fitz.Rect(0, page_rect.height - margin, page_rect.width, page_rect.height)
            
            # Redraw footer with correct total pages
            if footer_html:
                current_footer_html = footer_html.replace('{page_num}', str(current_content_page_num))
                current_footer_html = current_footer_html.replace('{total_pages}', str(total_pages_final))
                
                # Clear the old footer content by drawing a white rectangle over it
                page.draw_rect(footer_rect, color=(1,1,1), fill=(1,1,1))

                # Insert the new footer HTML with updated page numbers
                page.insert_htmlbox(footer_rect, current_footer_html, css=combined_css_content)

        try:
            doc.save(self.output_file)
        except Exception as e:
            logger.error(f"Error converting HTML to PDF with PyMuPDF: {e}")
            raise
        finally:
            doc.close() # Ensure the document is closed
        logger.info(f"Successfully converted '{self.input_file}' to '{self.output_file}'")