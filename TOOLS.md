# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 鬼哥的配置

### Email (SMTP)
- Provider: 163.com
- SMTP Server: smtp.163.com:465 (SSL)
- Sender: 山鬼之锤 <longbow_max@163.com>
- Default Recipient: longbow_max@163.com
- Auth Code: 存储于 tools/.email_auth（已设置权限保护）
- Scripts: 
  - `tools/email_sender.py` - 底层发送脚本
  - `tools/email_helper.py` - 便捷封装接口
