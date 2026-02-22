# OpenClaw 邮件发送工具封装
# 用法: from email_helper import send_email

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_sender import send_email as _send_email, set_auth_code, load_config

# 默认收件人（鬼哥的邮箱）
DEFAULT_RECIPIENT = "longbow_max@163.com"

def send_email(subject: str, body: str, recipient: str = None, html: str = None) -> bool:
    """
    发送邮件给鬼哥
    
    参数:
        subject: 邮件主题
        body: 邮件正文（纯文本）
        recipient: 收件人邮箱（默认: longbow_max@163.com）
        html: HTML格式正文（可选）
    
    返回:
        bool: 发送成功返回 True，失败返回 False
    
    示例:
        send_email("提醒", "该关注股票了！")
        send_email("报告", "今日分析报告", html="<h1>报告</h1><p>内容</p>")
    """
    if recipient is None:
        recipient = DEFAULT_RECIPIENT
    
    return _send_email(subject, body, recipient, html)

def send_notification(title: str, message: str) -> bool:
    """
    发送简单的通知邮件
    
    参数:
        title: 通知标题
        message: 通知内容
    
    示例:
        send_notification("股价预警", "南网储能股价跌破 10 元")
    """
    return send_email(f"[通知] {title}", message)

def send_report(report_title: str, content: str, is_html: bool = False) -> bool:
    """
    发送报告邮件
    
    参数:
        report_title: 报告标题
        content: 报告内容
        is_html: 内容是否为HTML格式
    
    示例:
        send_report("每日股票分析", "...报告内容...")
    """
    if is_html:
        return send_email(report_title, "请查看HTML格式的报告", html=content)
    else:
        return send_email(report_title, content)

# 测试
if __name__ == "__main__":
    # 测试邮件
    send_notification("邮件系统测试", "鬼哥，邮件发送功能已配置完成！")
