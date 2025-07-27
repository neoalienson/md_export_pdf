from abc import ABC, abstractmethod
from enum import Enum

class ProcessorType(Enum):
    MARKDOWN_PREPROCESSOR = "markdown_preprocessor"
    HTML_PREPROCESSOR = "html_preprocessor"
    PDF_POSTPROCESSOR = "pdf_postprocessor"

class BaseProcessor(ABC):
    def __init__(self, priority: int, processor_type: ProcessorType):
        self.priority = priority
        self.processor_type = processor_type

    @abstractmethod
    def process(self, *args, **kwargs):
        pass
