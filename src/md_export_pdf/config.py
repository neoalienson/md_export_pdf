from .md_preprocessor.front_matter import FrontMatterProcessor
from .md_preprocessor.mermaid import MermaidProcessor
from .md_preprocessor.code_block_processor import CodeBlockProcessor
from .pdf_postprocessors.pymupdf_header import PyMuPdfHeaderPostProcessor
from .pdf_postprocessors.pymupdf_footer import PyMuPdfFooterPostProcessor
from .pdf_postprocessors.dummy import DummyPostProcessor
from .pdf_postprocessors.data_classification_watermark import DataClassificationWatermarkPostProcessor
from .pdf_postprocessors.draft_watermark import DraftWatermarkPostProcessor
from .pdf_postprocessors.metadata_postprocessor import MetadataPostProcessor

MARKDOWN_PREPROCESSOR_PIPELINE = [
    FrontMatterProcessor(),
    MermaidProcessor(),
    CodeBlockProcessor(),
]

PDF_POSTPROCESSOR_PIPELINE = [
    PyMuPdfHeaderPostProcessor,
    PyMuPdfFooterPostProcessor,
    DummyPostProcessor,
    DataClassificationWatermarkPostProcessor,
    DraftWatermarkPostProcessor,
    MetadataPostProcessor,
]