# 邮件发送脚本 - OpenClaw Email Sender
# 使用方法: python email_sender.py "主题" "正文内容" [--to 收件人邮箱]

import smtplib
import ssl
import sys
import json
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "email_config.json"

def load_config():
    """加载邮件配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_config(config):
    """保存邮件配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def init_config():
    """初始化默认配置"""
    config = {
        "smtp_server": "smtp.163.com",
        "smtp_port": 465,
        "use_ssl": True,
        "sender_email": "longbow_max@163.com",
        "sender_name": "山鬼之锤",
        "default_recipient": "longbow_max@163.com"
    }
    save_config(config)
    return config

def get_auth_code():
    """从环境变量获取授权码"""
    # 优先从环境变量读取，确保安全
    auth_code = os.environ.get('EMAIL_AUTH_CODE')
    if not auth_code:
        # 如果环境变量没有，尝试从本地文件读取（已加密存储）
        auth_file = Path(__file__).parent / ".email_auth"
        if auth_file.exists():
            with open(auth_file, 'r') as f:
                auth_code = f.read().strip()
    return auth_code

def set_auth_code(auth_code):
    """设置授权码（保存到本地文件，仅当前用户可读写）"""
    auth_file = Path(__file__).parent / ".email_auth"
    with open(auth_file, 'w') as f:
        f.write(auth_code)
    # 设置文件权限，仅所有者可读写 (Windows 和 Linux/Mac 都适用)
    try:
        os.chmod(auth_file, 0o600)
    except:
        pass  # Windows 可能不支持此操作

def send_email(subject, body, recipient=None, html_body=None):
    """
    发送邮件
    
    参数:
        subject: 邮件主题
        body: 邮件正文（纯文本）
        recipient: 收件人邮箱（默认使用配置文件中的 default_recipient）
        html_body: HTML 格式正文（可选）
    """
    # 加载配置
    config = load_config()
    if not config:
        config = init_config()
    
    # 获取授权码
    auth_code = get_auth_code()
    if not auth_code:
        raise ValueError("未设置邮箱授权码！请先调用 set_auth_code()")
    
    # 确定收件人
    if not recipient:
        recipient = config.get('default_recipient', config['sender_email'])
    
    # 创建邮件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"{config['sender_name']} <{config['sender_email']}>"
    msg['To'] = recipient
    
    # 添加纯文本正文
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    
    # 添加 HTML 正文（如果提供）
    if html_body:
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    # 连接 SMTP 服务器并发送
    try:
        if config.get('use_ssl', True):
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port'], context=context) as server:
                server.login(config['sender_email'], auth_code)
                server.sendmail(config['sender_email'], recipient, msg.as_string())
        else:
            with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['sender_email'], auth_code)
                server.sendmail(config['sender_email'], recipient, msg.as_string())
        
        print(f"[OK] 邮件发送成功！")
        print(f"     收件人: {recipient}")
        print(f"     主题: {subject}")
        return True
        
    except Exception as e:
        print(f"[ERROR] 邮件发送失败: {e}")
        return False

def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python email_sender.py <主题> <正文> [--to 收件人邮箱]")
        print("示例: python email_sender.py '测试邮件' '这是一封测试邮件'")
        print("      python email_sender.py '测试邮件' '这是一封测试邮件' --to someone@example.com")
        sys.exit(1)
    
    subject = sys.argv[1]
    body = sys.argv[2]
    recipient = None
    
    # 解析命令行参数
    for i, arg in enumerate(sys.argv[3:], 3):
        if arg == '--to' and i + 1 < len(sys.argv):
            recipient = sys.argv[i + 1]
    
    send_email(subject, body, recipient)

if __name__ == "__main__":
    main()
