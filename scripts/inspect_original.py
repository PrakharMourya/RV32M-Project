import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = docx.Document(r'C:\Users\risha\Downloads\Block Diagram Report Guidelines_ORIGINAL.docx')
body = doc._body._body
print('Body child elements count:', len(body))
for idx, child in enumerate(body):
    tag = child.tag.split('}')[-1]
    if tag == 'p':
        text = ''.join(child.itertext()).strip()
        print(f'{idx:02d}: <p> "{text[:60]}"')
    elif tag == 'tbl':
        first_row = [''.join(c.itertext()).strip() for c in child.xpath('.//w:tr[1]//w:tc')]
        print(f'{idx:02d}: <tbl> First row: {first_row}')
    elif tag == 'sectPr':
        print(f'{idx:02d}: <sectPr>')
    else:
        print(f'{idx:02d}: <{tag}>')
