import pypdf

reader = pypdf.PdfReader(r'docs/word_rendered.pdf')
print(f'Total pages in Word PDF: {len(reader.pages)}')
for i, page in enumerate(reader.pages):
    text = page.extract_text().strip()
    first_line = text.split('\n')[0] if text else '[EMPTY OR ONLY IMAGE]'
    print(f'Page {i+1} ({len(text)} chars): {first_line[:80]}')
