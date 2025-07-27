import re
import logging
from ..base_processor import MarkdownPreprocessor

logger = logging.getLogger(__name__)

# Dictionary to store metadata for code blocks
_code_block_metadata = {}

class CodeBlockProcessor(MarkdownPreprocessor):
    def __init__(self, priority: int = 30):
        super().__init__(priority)

    def process(self, md_content: str) -> str:
        return self.process_markdown(md_content)

    def process_markdown(self, md_content):
        global _code_block_metadata
        _code_block_metadata = {}  # Clear previous metadata

        code_block_pattern = re.compile(
            r"^(```)(\w+)\s*(.*)?\n(.*?)\n^```\s*", re.MULTILINE | re.DOTALL
        )

        processed_content_parts = []
        last_end = 0
        block_id_counter = 0

        for match in code_block_pattern.finditer(md_content):
            start, end = match.span()
            processed_content_parts.append(md_content[last_end:start])

            opening_fence = match.group(1)
            lang = match.group(2).strip()
            attributes_str_on_line = match.group(3).strip()
            code_content = match.group(4)

            title = None
            linenums = False

            if attributes_str_on_line:
                if attributes_str_on_line.startswith("{") and attributes_str_on_line.endswith("}"):
                    clean_attributes_str = attributes_str_on_line.strip("{}").strip()
                else:
                    clean_attributes_str = attributes_str_on_line

                title_match = re.search(r'title="([^"]*)"|\'title\'', clean_attributes_str)
                if title_match:
                    title = (
                        title_match.group(1)
                        if title_match.group(1)
                        else title_match.group(0)
                    )

                if "linenums" in clean_attributes_str:
                    linenums = True

            current_block_id = f"code_block_{block_id_counter}"
            _code_block_metadata[current_block_id] = {
                "lang": lang,
                "title": title,
                "linenums": linenums,
            }

            processed_content_parts.append(
                f"{opening_fence}{lang}\n{code_content}\n```\n{{#{current_block_id}}}\n"
            )
            block_id_counter += 1
            last_end = end

        processed_content_parts.append(md_content[last_end:])
        return "".join(processed_content_parts)