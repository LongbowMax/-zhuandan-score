# OpenClaw 迁移指南

## 方案A：Git同步（推荐）

### 第1步：备份当前数据（旧电脑）

```powershell
# 1. 进入workspace目录
cd C:\Users\hp\.openclaw\workspace

# 2. 检查git状态
git status

# 3. 添加所有文件
git add .

# 4. 提交
git commit -m "迁移备份 - 更新所有记忆和项目"

# 5. 推送到GitHub（如果已配置远程仓库）
git push
```

如果没有配置远程仓库：
```powershell
# 创建GitHub仓库后
git remote add origin https://github.com/你的用户名/openclaw-backup.git
git push -u origin master
```

### 第2步：新电脑恢复

1. **安装OpenClaw**
   ```powershell
   npm install -g openclaw
   ```

2. **克隆workspace**
   ```powershell
   # 创建.openclaw目录
   mkdir C:\Users\你的用户名\.openclaw
   cd C:\Users\你的用户名\.openclaw
   
   # 克隆你的备份
   git clone https://github.com/你的用户名/openclaw-backup.git workspace
   ```

3. **复制其他配置文件**
   从旧电脑复制以下文件到新电脑对应位置：
   - `~/.openclaw/openclaw.json`
   - `~/.openclaw/identity/`
   - `~/.openclaw/skills/`（如果有自定义技能）

4. **启动OpenClaw**
   ```powershell
   openclaw
   ```

---

## 方案B：压缩包备份（简单）

### 旧电脑

```powershell
# 1. 备份整个.openclaw目录
Compress-Archive -Path C:\Users\hp\.openclaw -DestinationPath C:\Users\hp\Desktop\openclaw-backup.zip

# 2. 把zip文件复制到U盘或云盘
```

### 新电脑

1. 安装OpenClaw
2. 解压备份文件到 `C:\Users\你的用户名\.openclaw`
3. 启动OpenClaw

---

## 方案C：自动云同步（最省心）

### 使用OneDrive/Dropbox同步

1. **旧电脑**：把 `.openclaw` 文件夹放入OneDrive
2. **新电脑**：登录同一OneDrive账号，同步文件夹
3. **创建符号链接**（可选）：
   ```powershell
   # 如果.openclaw在其他位置，创建链接
   mklink /D C:\Users\你的用户名\.openclaw C:\Users\你的用户名\OneDrive\openclaw
   ```

---

## 📋 迁移检查清单

- [ ] workspace/ 目录已同步（包含记忆、项目）
- [ ] openclaw.json 已复制
- [ ] identity/ 已复制
- [ ] agents/ 已复制（可选）
- [ ] skills/ 已复制（如有自定义技能）
- [ ] 测试启动OpenClaw
- [ ] 验证记忆文件可读

---

## ⚠️ 注意事项

1. **绝对路径问题**：如果项目中有硬编码的路径，可能需要修改
2. **权限问题**：复制文件后可能需要重新设置权限
3. **API密钥**：如果openclaw.json中有API密钥，注意保密
4. **Git仓库**：子项目（如stock-risk-monitor）的git历史可能需要单独处理

---

## 🔄 日常自动备份建议

设置定期自动推送到GitHub：

```powershell
# 创建一个备份脚本 backup.ps1
cd C:\Users\hp\.openclaw\workspace
git add .
git commit -m "自动备份 - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push
```

然后用Windows任务计划程序每天自动运行。
