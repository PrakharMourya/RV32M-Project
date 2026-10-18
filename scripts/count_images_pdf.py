import pypdf

reader = pypdf.PdfReader(r'docs/test_clean_word.pdf')
for i, page in enumerate(reader.pages):
    print(f'Page {i+1} images count: {len(page.images)}')
