$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $docPath = "C:\Users\risha\OneDrive\Desktop\AutoVision\docs\Group21_Block_Diagram_Report.docx"
    $pdfPath = "C:\Users\risha\OneDrive\Desktop\AutoVision\docs\Group21_Block_Diagram_Report.pdf"
    $doc = $word.Documents.Open($docPath)
    $pageCount = $doc.ComputeStatistics(2) # 2 = wdStatisticPages
    Write-Host "Word Page Count: $pageCount"
    $doc.ExportAsFixedFormat($pdfPath, 17) # 17 = wdExportFormatPDF
    Write-Host "PDF exported to: $pdfPath"
    $doc.Close(0) # 0 = wdDoNotSaveChanges
} finally {
    $word.Quit()
}
