from .md_preprocessor.front_matter import FrontMatterProcessor
from .md_preprocessor.mermaid import MermaidProcessor
from .md_preprocessor.code_block_processor import CodeBlockProcessor

MARKDOWN_PREPROCESSOR_PIPELINE = [
    FrontMatterProcessor(),
    MermaidProcessor(),
    CodeBlockProcessor(),
]
