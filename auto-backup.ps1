# OpenClaw Workspace 自动备份脚本
# 保存为: C:\Users\hp\.openclaw\workspace\auto-backup.ps1

# 设置工作目录
$workspacePath = "C:\Users\hp\.openclaw\workspace"
Set-Location $workspacePath

# 获取当前时间
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

# 检查是否有更改
$status = git status --porcelain

if ($status) {
    Write-Host "检测到更改，开始备份..." -ForegroundColor Green
    
    # 添加所有更改
    git add .
    
    # 提交
    git commit -m "自动备份 - $timestamp"
    
    # 推送到GitHub
    git push origin master
    
    Write-Host "备份完成: $timestamp" -ForegroundColor Green
} else {
    Write-Host "没有需要备份的更改" -ForegroundColor Yellow
}
