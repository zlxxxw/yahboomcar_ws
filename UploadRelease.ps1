#!/usr/bin/env powershell

# 注意: Token 应该通过参数或环境变量传递，不要硬编码
param([string]$Token)

if (-not $Token) {
    $Token = $env:GITHUB_TOKEN
}

if (-not $Token) {
    Write-Error "Please provide GitHub token via -Token parameter or GITHUB_TOKEN environment variable"
    exit 1
}

$ReleaseId = 321074744
$Owner = "zlxxxw"
$Repo = "yahboomcar_ws"

$Headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

# 获取 Release 上传 URL
$Release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Owner/$Repo/releases/$ReleaseId" -Headers $Headers
$UploadUrl = $Release.upload_url -replace '\{.*?\}', ''

Write-Output "上传 URL: $UploadUrl"

# 文件列表
$Files = @(
    "src/yahboomcar_slam/param/ORBvoc.txt",
    "src/yahboomcar_slam/resultPointCloudFile.pcd", 
    "src/yahboomcar_mediapipe/scripts/file/shape_predictor_68_face_landmarks.dat",
    "src/yahboomcar_visual/detection/frozen_inference_graph.pb"
)

foreach ($File in $Files) {
    $FileName = Split-Path $File -Leaf
    
    if (-not (Test-Path $File)) {
        Write-Output "跳过: $FileName (不存在)"
        continue
    }
    
    $Item = Get-Item $File
    $SizeMB = [math]::Round($Item.Length / 1MB, 2)
    
    Write-Output "上传: $FileName ($SizeMB MB)..."
    
    try {
        $FileContent = [System.IO.File]::ReadAllBytes($File)
        $UploadUri = "$UploadUrl`?name=$FileName"
        
        $UploadHeaders = @{
            "Authorization" = "token $Token"
            "Content-Type" = "application/octet-stream"
        }
        
        $Response = Invoke-RestMethod -Uri $UploadUri -Method Post -Headers $UploadHeaders -Body $FileContent -TimeoutSec 3600
        Write-Output "OK: $FileName (Asset ID: $($Response.id))"
    } catch {
        Write-Output "失败: $FileName - $_"
    }
}

Write-Output ""
Write-Output "完成! Release: https://github.com/$Owner/$Repo/releases/tag/v1.0"
