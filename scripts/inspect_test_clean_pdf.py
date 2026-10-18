import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')
reader = pypdf.PdfReader(r'docs/test_clean_word.pdf')
print(f'Test Clean Word PDF Page Count: {len(reader.pages)}')
for i, page in enumerate(reader.pages):
    text = page.extract_text().strip()
    lines = text.split('\n')
    print(f'=== Page {i+1} ({len(text)} chars) ===')
    for line in lines[:3]:
        print('  ', line[:80])
