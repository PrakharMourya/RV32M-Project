import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = docx.Document(r'C:\Users\risha\Downloads\Block Diagram Report Guidelines_ORIGINAL.docx')

print('=== STYLES DEFINED IN ORIGINAL DOCX ===')
for s in doc.styles:
    if s.type == docx.enum.style.WD_STYLE_TYPE.PARAGRAPH:
        font_name = s.font.name if s.font else None
        font_size = s.font.size.pt if s.font and s.font.size else None
        print(f'Style: "{s.name}", base="{s.base_style.name if s.base_style else None}", font={font_name}, sz={font_size}')

print('\n=== PARAGRAPH 0 TO 10 RUN PROPERTIES ===')
for i in range(10):
    p = doc.paragraphs[i]
    print(f'P{i:02d}: style="{p.style.name}"')
    for r in p.runs:
        print(f'   run: text="{r.text}", font={r.font.name}, sz={r.font.size.pt if r.font.size else None}, bold={r.bold}, italic={r.italic}')
