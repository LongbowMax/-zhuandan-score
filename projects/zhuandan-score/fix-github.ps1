# 修复GitHub Actions路径问题的完整命令
# 在PowerShell中执行

# 第1步：进入项目目录
cd C:\Users\hp\.openclaw\workspace\projects\zhuandan-score

# 第2步：删除旧的git历史（因为之前的提交结构不对）
Remove-Item -Recurse -Force .git

# 第3步：重新初始化git
git init

# 第4步：配置git用户信息（如果还没配置）
git config user.email "zhuandan@example.com"
git config user.name "ZhuanDan Builder"

# 第5步：添加所有文件
git add .

# 第6步：提交
git commit -m "Initial commit with GitHub Actions"

# 第7步：添加远程仓库（把你的用户名替换进去）
# 注意：把 YOUR_GITHUB_USERNAME 换成你的GitHub用户名
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/zhuandan-score.git

# 第8步：推送到GitHub
git push -u origin master --force

Write-Host "完成！现在去GitHub查看Actions标签页" -ForegroundColor Green
