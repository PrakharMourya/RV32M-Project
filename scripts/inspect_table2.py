import docx
import sys

sys.stdout.reconfigure(encoding='utf-8')
doc = docx.Document(r'C:\Users\risha\Downloads\Block Diagram Report Guidelines_ORIGINAL.docx')

t2 = doc.tables[2]
print(f'Table 2 rows: {len(t2.rows)}, cols: {len(t2.columns)}')
for r_idx in range(min(5, len(t2.rows))):
    row = t2.rows[r_idx]
    widths = [c.width for c in row.cells]
    print(f'Row {r_idx} cell widths (sample first 6): {widths[:6]}')
    texts = [c.text.strip() for c in row.cells]
    print(f'Row {r_idx} text (sample first 6): {texts[:6]}')

# Check table grid
tblGrid = t2._tbl.tblGrid
if tblGrid is not None:
    gridCols = [col.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}w') for col in tblGrid.gridCol_lst]
    print(f'tblGrid col count: {len(gridCols)}, first 6: {gridCols[:6]}')

# Check table properties
tblPr = t2._tbl.tblPr
print('tblPr XML:')
print(tblPr.xml)
