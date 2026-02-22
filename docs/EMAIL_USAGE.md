# 📧 邮件发送功能使用指南

## 配置信息

| 项目 | 值 |
|------|-----|
| 邮箱提供商 | 163.com |
| SMTP 服务器 | smtp.163.com:465 (SSL) |
| 发件人 | 山鬼之锤 <longbow_max@163.com> |
| 默认收件人 | longbow_max@163.com |
| 授权码存储 | `tools/.email_auth` |

## 使用方法

### 1. 快速发送邮件（推荐）

```python
# 在 Python 中调用
from tools.email_helper import send_email, send_notification

# 发送普通邮件
send_email(
    subject="股票预警",
    body="南网储能股价触发预警，请及时关注！"
)

# 发送通知（带[通知]前缀）
send_notification(
    title="提醒",
    message="该关注股票了！"
)
```

### 2. 命令行发送

```bash
# 进入 tools 目录
cd tools

# 发送简单邮件
python email_sender.py "测试邮件" "这是邮件内容"

# 发送给指定收件人
python email_sender.py "测试邮件" "这是邮件内容" --to someone@example.com
```

### 3. 在其他脚本中使用

```python
import sys
sys.path.insert(0, 'tools')
from email_helper import send_email

# 发送纯文本邮件
send_email("标题", "正文内容")

# 发送 HTML 邮件
html_content = """
<h1 style="color: red;">紧急预警</h1>
<p>南网储能股价跌破 10 元！</p>
"""
send_email("股价预警", "请查看 HTML 报告", html=html_content)
```

## 使用场景示例

### 股票监控通知
```python
from tools.email_helper import send_notification

# 当股价触发条件时
if stock_price < warning_price:
    send_notification(
        title=f"股价预警 - {stock_name}",
        message=f"当前价格: {stock_price}\n预警价格: {warning_price}\n请及时关注！"
    )
```

### 定期报告
```python
from tools.email_helper import send_report

# 发送每日分析报告
send_report(
    report_title="每日股票分析报告",
    content=report_text
)
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `tools/email_sender.py` | 底层 SMTP 发送脚本 |
| `tools/email_helper.py` | 便捷封装接口 |
| `tools/email_config.json` | 邮件配置（非敏感信息） |
| `tools/.email_auth` | 授权码（已设置权限保护） |

## 安全说明

- ✅ 授权码存储在 `.email_auth` 文件，已设置仅当前用户可读写
- ✅ 配置文件与代码分离
- ✅ 支持环境变量覆盖敏感信息

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 发送失败，提示认证错误 | 检查授权码是否正确（注意不是登录密码） |
| 提示 SSL 错误 | 检查网络连接或尝试关闭防火墙 |
| 中文乱码 | 脚本已设置 UTF-8 编码，确保邮件客户端支持 |

---
⚒️🏔️ 由山鬼之锤配置 | 2026-02-21
