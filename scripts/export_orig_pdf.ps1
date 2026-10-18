$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('C:\Users\risha\Downloads\Block Diagram Report Guidelines_ORIGINAL.docx')
    $doc.ExportAsFixedFormat('C:\Users\risha\OneDrive\Desktop\AutoVision\docs\orig_template.pdf', 17)
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
