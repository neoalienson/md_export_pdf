import markdown

md_table = """
| Header 1 | Header 2 |
|----------|----------|
| Row 1    | Row 2    |
"""

html_output = markdown.Markdown(extensions=['tables']).convert(md_table)
print(html_output)
