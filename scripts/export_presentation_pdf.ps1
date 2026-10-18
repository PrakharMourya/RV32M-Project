$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
try {
    $pptxPath = "C:\Users\risha\OneDrive\Desktop\AutoVision\docs\AutoVision_Presentation.pptx"
    $pdfPath = "C:\Users\risha\OneDrive\Desktop\AutoVision\docs\AutoVision_Presentation.pdf"
    $pdfDL = "C:\Users\risha\Downloads\AutoVision_Presentation.pdf"
    $pdfBrain = "C:\Users\risha\.gemini\antigravity\brain\685340e0-fa4d-40ef-a8cb-ccfb71d7e1bc\AutoVision_Presentation.pdf"
    $slidesDir = "C:\Users\risha\OneDrive\Desktop\AutoVision\docs\presentation_slides"

    if (-not (Test-Path $slidesDir)) {
        New-Item -ItemType Directory -Path $slidesDir | Out-Null
    }

    $pres = $ppt.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    Write-Host "Presentation opened. Slide count: " $pres.Slides.Count

    # Export to PDF (32 = ppSaveAsPDF)
    $pres.SaveAs($pdfPath, 32)
    Write-Host "PDF exported to: " $pdfPath
    Copy-Item -Path $pdfPath -Destination $pdfDL -Force
    Copy-Item -Path $pdfPath -Destination $pdfBrain -Force

    # Export each slide as high-res PNG (1920x1080)
    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $slidePng = Join-Path $slidesDir ("slide_" + $i + ".png")
        $pres.Slides.Item($i).Export($slidePng, "PNG", 1920, 1080)
        Write-Host ("Exported slide " + $i + " to: " + $slidePng)
    }

    $pres.Close()
} finally {
    $ppt.Quit()
}
