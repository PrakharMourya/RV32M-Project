$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open('C:\Users\risha\Downloads\Block Diagram Report Guidelines_ORIGINAL.docx')
    $pages = $doc.ComputeStatistics(2)
    Write-Output "Original Template Page Count: $pages"
    $doc.Close([ref]$false)
} finally {
    $word.Quit()
}
