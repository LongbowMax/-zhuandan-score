"""
A股风险预警系统 - 通知模块 V2
支持：控制台、微信（Server酱）
"""
import json
import requests
from datetime import datetime

class Notifier:
    """风险通知器"""
    
    def __init__(self, config_path='../config/settings.json'):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.enabled = self.config.get('notification', {}).get('enabled', True)
        self.channels = self.config.get('notification', {}).get('channels', ['console'])
    
    def send_alert(self, stock_name, stock_code, risk_summary, config):
        """发送个股风险预警"""
        if not self.enabled:
            return
        
        message = self._format_stock_message(stock_name, stock_code, risk_summary)
        
        for channel in self.channels:
            if channel == 'console':
                self._send_to_console(message)
            elif channel == 'wechat':
                self._send_to_wechat(message, stock_name, risk_summary)
    
    def send_macro_alert(self, macro_summary, config):
        """发送宏观经济预警"""
        if not self.enabled:
            return
        
        message = self._format_macro_message(macro_summary)
        
        for channel in self.channels:
            if channel == 'console':
                self._send_to_console(message)
            elif channel == 'wechat':
                self._send_to_wechat(message, "宏观经济", {'level': macro_summary.get('level', 'low')})
    
    def _format_stock_message(self, stock_name, stock_code, risk_summary):
        """格式化个股预警消息"""
        level_emoji = {'high': '!!', 'medium': '! ', 'low': 'OK', 'safe': 'OK'}
        
        level = risk_summary.get('level', 'low')
        emoji = level_emoji.get(level, '--')
        
        lines = [
            f"[{emoji}] A股风险预警: {stock_name} ({stock_code})",
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"风险等级: {level.upper()}",
            f"评估结果: {risk_summary.get('message', '')}",
            ""
        ]
        
        risks = risk_summary.get('risks', [])
        if risks:
            lines.append("发现的风险项：")
            for i, risk in enumerate(risks[:5], 1):
                risk_level = risk.get('level', 'low')
                risk_emoji = {'high': '!!', 'medium': '! ', 'low': '-'}.get(risk_level, '--')
                lines.append(f"{i}. [{risk_emoji}] {risk.get('type', '')}")
                lines.append(f"   {risk.get('desc', '')}")
        else:
            lines.append("未发现明显风险")
        
        lines.append("")
        lines.append("—— 山鬼之锤")
        
        return '\n'.join(lines)
    
    def _format_macro_message(self, macro_summary):
        """格式化宏观经济预警消息"""
        level_emoji = {'high': '!!', 'medium': '! ', 'low': 'OK', 'safe': 'OK'}
        
        level = macro_summary.get('level', 'low')
        emoji = level_emoji.get(level, '--')
        
        lines = [
            f"[{emoji}] 宏观经济预警",
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"风险等级: {level.upper()}",
            f"评估结果: {macro_summary.get('message', '')}",
            ""
        ]
        
        alerts = macro_summary.get('alerts', [])
        if alerts:
            lines.append("宏观指标异常：")
            for i, alert in enumerate(alerts[:5], 1):
                alert_level = alert.get('level', 'low')
                alert_emoji = {'high': '!!', 'medium': '! ', 'low': '-'}.get(alert_level, '--')
                lines.append(f"{i}. [{alert_emoji}] {alert.get('type', '')} ({alert.get('indicator', '')})")
                lines.append(f"   {alert.get('desc', '')}")
        
        lines.append("")
        lines.append("—— 山鬼之锤")
        
        return '\n'.join(lines)
    
    def _send_to_console(self, message):
        """输出到控制台"""
        print("\n" + "-"*50)
        print(message)
        print("-"*50 + "\n")
    
    def _send_to_wechat(self, message, title, risk_info):
        """发送到微信（通过Server酱）"""
        wechat_config = self.config.get('notification', {}).get('wechat', {})
        
        if not wechat_config.get('enabled', False):
            return
        
        send_key = wechat_config.get('send_key', '')
        if not send_key:
            return
        
        try:
            url = f"https://sctapi.ftqq.com/{send_key}.send"
            
            # 根据风险等级选择消息模板
            level = risk_info.get('level', 'low')
            if level == 'high':
                msg_title = f"【紧急】{title} 高风险预警"
            elif level == 'medium':
                msg_title = f"【注意】{title} 风险提醒"
            else:
                msg_title = f"【正常】{title} 每日监控"
            
            data = {
                'title': msg_title,
                'desp': message.replace('\n', '\n\n')
            }
            
            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    print(f"    [微信] 推送成功")
                else:
                    print(f"    [微信] 推送失败: {result.get('message', '未知错误')}")
            else:
                print(f"    [微信] 请求失败: {response.status_code}")
        except Exception as e:
            print(f"    [微信] 发送异常: {e}")

if __name__ == '__main__':
    # 测试
    notifier = Notifier()
    
    # 测试个股预警
    test_stock = {
        'level': 'high',
        'message': '发现2项高风险',
        'risks': [
            {'level': 'high', 'type': '净利润大幅下滑', 'desc': '净利润同比下降35%'}
        ]
    }
    notifier.send_alert("南网储能", "600995", test_stock, {})
