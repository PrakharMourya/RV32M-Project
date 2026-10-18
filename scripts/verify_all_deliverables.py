import os, pypdf, docx

files_to_check = [
    r'C:\Users\risha\Downloads\Block Diagram Report Guidelines.docx',
    r'C:\Users\risha\Downloads\Group21_Block_Diagram_Report.docx',
    r'C:\Users\risha\Downloads\Group21_Block_Diagram_Report.pdf',
    r'C:\Users\risha\OneDrive\Desktop\AutoVision\docs\Group21_Block_Diagram_Report.docx',
    r'C:\Users\risha\OneDrive\Desktop\AutoVision\docs\Group21_Block_Diagram_Report.pdf',
    r'C:\Users\risha\.gemini\antigravity\brain\685340e0-fa4d-40ef-a8cb-ccfb71d7e1bc\Group21_Block_Diagram_Report.docx',
    r'C:\Users\risha\.gemini\antigravity\brain\685340e0-fa4d-40ef-a8cb-ccfb71d7e1bc\Group21_Block_Diagram_Report.pdf'
]

print("=== DELIVERABLE STATUS AUDIT ===")
for f in files_to_check:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    print(f"{os.path.basename(f)} [{os.path.dirname(f)}]: exists={exists}, size={size:,} bytes")

pdf_path = r'C:\Users\risha\OneDrive\Desktop\AutoVision\docs\Group21_Block_Diagram_Report.pdf'
reader = pypdf.PdfReader(pdf_path)
print(f"\nTotal Rendered PDF Pages: {len(reader.pages)}")

# Student anonymity check
doc = docx.Document(r'C:\Users\risha\OneDrive\Desktop\AutoVision\docs\Group21_Block_Diagram_Report.docx')
doc_text = ' '.join([p.text for p in doc.paragraphs] + [c.text for t in doc.tables for r in t.rows for c in r.cells])
names = ['Rishabh', 'Rohit', 'Sarthak', 'Sajan', 'Harsh']
print("\n=== ANONYMITY AUDIT ===")
for n in names:
    cnt = doc_text.lower().count(n.lower())
    print(f"Name '{n}': {cnt} occurrences (Strict Pass: 0)")
