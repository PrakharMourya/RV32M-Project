import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')
reader = pypdf.PdfReader(r'docs/orig_template.pdf')
print(f'Original Template PDF Page Count: {len(reader.pages)}')
for i, page in enumerate(reader.pages):
    text = page.extract_text().strip()
    lines = text.split('\n')
    print(f'=== Page {i+1} ({len(text)} chars) ===')
    for line in lines[:5]:
        print('  ', line[:80])
