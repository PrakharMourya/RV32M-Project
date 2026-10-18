try {
    $ppt = New-Object -ComObject PowerPoint.Application
    Write-Host "PowerPoint COM Available, Version:" $ppt.Version
    $ppt.Quit()
} catch {
    Write-Host "PowerPoint COM Error:" $_
}
