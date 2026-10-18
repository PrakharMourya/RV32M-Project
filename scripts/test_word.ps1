$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('C:\Users\risha\OneDrive\Desktop\AutoVision\docs\test_4page.docx')
    $doc.ExportAsFixedFormat('C:\Users\risha\OneDrive\Desktop\AutoVision\docs\test_4page_word.pdf', 17)
    $pages = $doc.ComputeStatistics(2)
    Write-Output "Word Page Count for test_4page: $pages"
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
