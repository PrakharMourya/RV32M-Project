import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = docx.Document(r'C:\Users\risha\Downloads\Block Diagram Report Guidelines_ORIGINAL.docx')

print("Paragraphs in original template:")
for i, p in enumerate(doc.paragraphs):
    print(f"P{i:02d} [{p.style.name}]: '{p.text}'")
