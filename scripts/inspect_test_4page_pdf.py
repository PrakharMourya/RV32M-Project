import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')
reader = pypdf.PdfReader(r'docs/test_4page_word.pdf')
print(f'Test 4Page Word PDF Page Count: {len(reader.pages)}')
for i, page in enumerate(reader.pages):
    text = page.extract_text().strip()
    first_line = text.split('\n')[0] if text else '[ONLY IMAGE]'
    print(f'Page {i+1} ({len(text)} chars): {first_line[:80]}')
