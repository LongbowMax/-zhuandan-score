# Windows定时自动备份设置指南

## 方法1：手动运行备份脚本

每次想备份时，打开PowerShell执行：
```powershell
cd C:\Users\hp\.openclaw\workspace
.\auto-backup.ps1
```

## 方法2：设置Windows定时任务（每天自动备份）

### 步骤1：打开任务计划程序

1. 按 `Win + R`，输入 `taskschd.msc`，回车
2. 点击右侧 "创建基本任务"

### 步骤2：配置任务

**名称**: OpenClaw自动备份  
**描述**: 每天自动备份workspace到GitHub  
**触发器**: 每天  
**时间**: 建议选择深夜（如 23:00）  
**操作**: 启动程序  

**程序/脚本**: 
```
powershell.exe
```

**参数**: 
```
-ExecutionPolicy Bypass -File "C:\Users\hp\.openclaw\workspace\auto-backup.ps1"
```

### 步骤3：完成

点击完成，任务就会每天自动运行。

### 步骤4：测试

右键点击创建的任务 → "运行"，测试是否能正常备份。

---

## 常见问题

**Q: 提示没有权限运行脚本？**  
A: 以管理员身份运行PowerShell，执行：
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Q: 推送时要求输入密码？**  
A: 需要配置Git凭证管理器，或使用SSH密钥。最简单的办法是先用GitHub Desktop登录一次。

**Q: 备份失败怎么知道？**  
A: 可以在脚本中添加发送邮件通知的功能（需要配置SMTP）。

---

## 查看备份记录

```powershell
cd C:\Users\hp\.openclaw\workspace
git log --oneline -10
```
