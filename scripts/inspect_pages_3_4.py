import pypdf
import sys

sys.stdout.reconfigure(encoding='utf-8')
reader = pypdf.PdfReader(r'docs/test_clean_word.pdf')
print('Page 3 text:', reader.pages[2].extract_text()[:400])
print('Page 4 text:', reader.pages[3].extract_text()[:400])
