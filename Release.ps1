param([string]$Token)

if (-not $Token) {
    $Token = $env:GITHUB_TOKEN
}

if (-not $Token) {
    Write-Error "Please provide GitHub token via -Token parameter or GITHUB_TOKEN environment variable"
    exit 1
}

$Owner = "zlxxxw"
$Repo = "yahboomcar_ws"
$Tag = "v1.0"
$Name = "YahBoomCar Large Files - v1.0"

$Headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

$Body = @{
    tag_name = $Tag
    target_commitish = "main"
    name = $Name
    body = "Large data files: ORBvoc.txt, resultPointCloudFile.pcd, shape_predictor_68_face_landmarks.dat, frozen_inference_graph.pb"
    draft = $false
    prerelease = $false
} | ConvertTo-Json

Write-Host "Creating release..." -ForegroundColor Green

$ReleaseUrl = "https://api.github.com/repos/$Owner/$Repo/releases"
$Release = Invoke-RestMethod -Uri $ReleaseUrl -Method Post -Headers $Headers -Body $Body -ContentType "application/json"

Write-Host "Release created! ID: $($Release.id)" -ForegroundColor Green

$UploadUrl = $Release.upload_url -replace '\{.*?\}', ''

$Files = @(
    "C:\Users\dell\Desktop\新建文件夹\GSE\yahboomcar_ws\src\yahboomcar_slam\param\ORBvoc.txt",
    "C:\Users\dell\Desktop\新建文件夹\GSE\yahboomcar_ws\src\yahboomcar_slam\resultPointCloudFile.pcd",
    "C:\Users\dell\Desktop\新建文件夹\GSE\yahboomcar_ws\src\yahboomcar_mediapipe\scripts\file\shape_predictor_68_face_landmarks.dat",
    "C:\Users\dell\Desktop\新建文件夹\GSE\yahboomcar_ws\src\yahboomcar_visual\detection\frozen_inference_graph.pb"
)

foreach ($File in $Files) {
    if (Test-Path $File) {
        $FileName = Split-Path $File -Leaf
        $Size = (Get-Item $File).Length / 1MB
        Write-Host "Uploading $FileName ($([math]::Round($Size, 2)) MB)..." -ForegroundColor Cyan
        
        $FileContent = [System.IO.File]::ReadAllBytes($File)
        $UploadHeaders = $Headers.Clone()
        $UploadHeaders["Content-Type"] = "application/octet-stream"
        
        $AssetUrl = "$UploadUrl`?name=$FileName"
        Invoke-RestMethod -Uri $AssetUrl -Method Post -Headers $UploadHeaders -Body $FileContent | Out-Null
        
        Write-Host "OK: $FileName" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Success! Release URL: https://github.com/$Owner/$Repo/releases/tag/$Tag" -ForegroundColor Green
