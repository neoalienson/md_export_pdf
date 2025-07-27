import fitz
import logging
import os
import traceback
import io
from typing import Dict, Any
from PIL import Image  # Import Pillow's Image module

from .base import PdfPostProcessor

logger = logging.getLogger(__name__)


class DraftWatermarkPostProcessor(PdfPostProcessor):
    def __init__(self, converter_instance: Any, priority: int = 90):
        super().__init__(converter_instance, priority)
        self.logger = logging.getLogger(__name__)

    def should_apply(self, converter_instance: Any, front_matter_data: Dict) -> bool:
        return front_matter_data.get("draft", False)

    def get_process_options(self, converter_instance: Any, front_matter_data: Dict) -> Dict:
        return {}

    def process(self, pdf_path: str, options: Dict) -> None:
        self.logger.debug(
            f"DraftWatermarkPostProcessor: Applying watermark to {pdf_path}"
        )

        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        self.logger.debug(f"Total pages in PDF: {num_pages}")

        watermark_text = "DRAFT"
        font_size = 128  # Large font size
        rotation_angle = 60  # degrees anti-clockwise
        transparency = 0.25  # 25% transparent

        for i, page in enumerate(doc):
            self.logger.debug(f"Processing page {i+1} of {num_pages} for watermark.")

            page_width = page.rect.width
            page_height = page.rect.height

            # Create a temporary page to draw the watermark text on
            temp_watermark_page = fitz.open().new_page(
                width=page_width, height=page_height
            )

            # Draw the text on the temporary page without rotation
            # Position it roughly in the center
            text_x = page_width / 2 - (
                font_size * len(watermark_text) * 0.3
            )  # Rough center adjustment
            text_y = page_height / 2 - (font_size / 2)

            temp_watermark_page.insert_text(
                (text_x, text_y),
                watermark_text,
                fontname="helv",
                fontsize=font_size,
                color=(0, 0, 0),  # Black color
            )

            # Get a pixmap of the temporary page
            watermark_pix = temp_watermark_page.get_pixmap(alpha=True)

            # Convert fitz.Pixmap to PIL Image
            img = Image.frombytes(
                "RGBA",
                [watermark_pix.width, watermark_pix.height],
                watermark_pix.samples,
            )

            # Rotate the PIL Image
            rotated_img = img.rotate(
                rotation_angle, expand=True, fillcolor=(0, 0, 0, 0)
            )

            # Apply transparency to the rotated PIL Image
            # Create a new image with alpha channel if it doesn't exist
            if rotated_img.mode != "RGBA":
                rotated_img = rotated_img.convert("RGBA")

            # Get the alpha channel
            alpha = rotated_img.split()[3]  # Get the alpha channel (4th channel)
            # Apply transparency factor
            alpha = Image.eval(
                alpha, lambda x: x * transparency
            )  # Apply transparency to each pixel

            # Merge the modified alpha channel back into the image
            rotated_img.putalpha(alpha)

            # Convert PIL Image back to fitz.Pixmap
            # Save to a BytesIO object first
            img_byte_arr = io.BytesIO()
            rotated_img.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)

            # Create fitz.Pixmap from PNG bytes
            final_watermark_pix = fitz.Pixmap(img_byte_arr.read())

            # Calculate position to insert the rotated pixmap onto the actual page
            # This will center the rotated pixmap on the page
            insert_point_x = (page_width - final_watermark_pix.width) / 2
            insert_point_y = (page_height - final_watermark_pix.height) / 2

            page.insert_image(
                fitz.Rect(
                    insert_point_x,
                    insert_point_y,
                    insert_point_x + final_watermark_pix.width,
                    insert_point_y + final_watermark_pix.height,
                ),
                pixmap=final_watermark_pix,
            )

        self.logger.debug(f"Saving modified PDF to {pdf_path}")
        temp_output_path = pdf_path + ".tmp"
        doc.save(temp_output_path)
        doc.close()
        os.replace(temp_output_path, pdf_path)
        self.logger.debug(f"PDF saved and replaced successfully.")
