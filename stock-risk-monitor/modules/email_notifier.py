"""
A股风险预警系统 - 邮件通知模块 V3.0
整合邮件发送功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from typing import Dict, List, Optional

from email_reporter import EmailReporter
from macro_report_generator import MacroReportGenerator

# 导入邮件发送工具
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'tools'))
from email_helper import send_email

class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self, config_path='../config/settings.json'):
        self.config = self._load_config(config_path)
        self.reporter = EmailReporter(config_path)
        self.email_config = self.config.get('notification', {}).get('email', {})
        self.enabled = self.email_config.get('enabled', False)
        self.recipients = self.email_config.get('recipients', ['longbow_max@163.com'])
    
    def _load_config(self, path):
        """加载配置"""
        full_path = os.path.join(os.path.dirname(__file__), path)
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def send_risk_alert(self, stock_name: str, stock_code: str, 
                        risk_summary: Dict, all_risks: List[Dict],
                        daily_data: Optional[Dict] = None) -> bool:
        """
        发送风险预警邮件
        
        参数:
            stock_name: 股票名称
            stock_code: 股票代码
            risk_summary: 风险摘要
            all_risks: 所有风险项列表
            daily_data: 行情数据（可选）
        
        返回:
            bool: 是否发送成功
        """
        if not self.enabled:
            print("    [邮件] 邮件通知未启用")
            return False
        
        try:
            # 生成邮件内容
            email = self.reporter.generate_risk_alert_email(
                stock_name, stock_code, risk_summary, all_risks, daily_data
            )
            
            # 发送给所有收件人
            success_count = 0
            for recipient in self.recipients:
                result = send_email(
                    subject=email['subject'],
                    body=email['text'],
                    recipient=recipient,
                    html=email['html']
                )
                if result:
                    success_count += 1
            
            if success_count == len(self.recipients):
                print(f"    [邮件] 预警邮件发送成功 ({success_count}/{len(self.recipients)})")
                return True
            elif success_count > 0:
                print(f"    [邮件] 部分发送成功 ({success_count}/{len(self.recipients)})")
                return True
            else:
                print(f"    [邮件] 发送失败")
                return False
                
        except Exception as e:
            print(f"    [邮件] 发送异常: {e}")
            return False
    
    def send_daily_report(self, stocks_data: List[Dict], report_date: datetime = None) -> bool:
        """
        发送每日监控报告
        
        参数:
            stocks_data: 各股票分析结果列表
            report_date: 报告日期（默认今天）
        
        返回:
            bool: 是否发送成功
        """
        if not self.enabled:
            print("    [邮件] 邮件通知未启用")
            return False
        
        if report_date is None:
            report_date = datetime.now()
        
        try:
            # 生成日报
            email = self.reporter.generate_daily_report_email(report_date, stocks_data)
            
            # 发送给所有收件人
            success_count = 0
            for recipient in self.recipients:
                result = send_email(
                    subject=email['subject'],
                    body=email['text'],
                    recipient=recipient,
                    html=email['html']
                )
                if result:
                    success_count += 1
            
            if success_count > 0:
                print(f"    [邮件] 日报发送成功 ({success_count}/{len(self.recipients)})")
                return True
            else:
                print(f"    [邮件] 日报发送失败")
                return False
                
        except Exception as e:
            print(f"    [邮件] 日报发送异常: {e}")
            return False
    
    def send_macro_alert(self, macro_summary: Dict, indicators_data: Dict = None) -> bool:
        """
        发送宏观经济报告邮件
        
        参数:
            macro_summary: 宏观经济分析结果
            indicators_data: 详细指标数据（可选）
        
        返回:
            bool: 是否发送成功
        """
        if not self.enabled:
            return False
        
        try:
            # 使用新的报告生成器
            generator = MacroReportGenerator()
            report = generator.generate_macro_report(macro_summary, indicators_data)
            
            # 发送给所有收件人
            success_count = 0
            for recipient in self.recipients:
                result = send_email(
                    subject=report['subject'],
                    body=report['text'],
                    recipient=recipient,
                    html=report['html']
                )
                if result:
                    success_count += 1
            
            if success_count > 0:
                print(f"    [邮件] 宏观报告发送成功 ({success_count}/{len(self.recipients)})")
                return True
            else:
                print(f"    [邮件] 宏观报告发送失败")
                return False
                
        except Exception as e:
            print(f"    [邮件] 宏观报告发送异常: {e}")
            return False
    
    def should_send_alert(self, risk_level: str) -> bool:
        """
        判断是否应该发送预警
        
        规则：
        - 高风险：始终发送
        - 中风险：始终发送
        - 低风险：不发送（只在日报中显示）
        
        参数:
            risk_level: 风险等级 (high/medium/low)
        
        返回:
            bool: 是否应该发送
        """
        if risk_level in ['high', 'medium']:
            return True
        return False


if __name__ == '__main__':
    # 测试邮件通知
    print("测试邮件通知模块...")
    
    notifier = EmailNotifier()
    
    # 测试风险预警
    test_risks = [
        {'level': 'high', 'type': '净利润大幅下滑', 'desc': '净利润同比下降35%，超过预警阈值'},
    ]
    test_summary = {
        'level': 'high',
        'message': '发现高风险，建议减仓观望',
        'risks': test_risks
    }
    
    print("\n1. 测试风险预警邮件:")
    notifier.send_risk_alert("南网储能", "600995", test_summary, test_risks)
    
    # 测试日报
    print("\n2. 测试日报邮件:")
    test_stocks = [
        {'name': '南网储能', 'code': '600995', 'position': 0.7, 'risk_level': 'high', 'change_pct': -2.5, 'close': 9.85, 'volume': '12.5万手', 'risk_count': 2},
        {'name': '大禹节水', 'code': '300021', 'position': 0, 'risk_level': 'low', 'change_pct': 1.2, 'close': 4.25, 'volume': '5.3万手', 'risk_count': 0},
    ]
    notifier.send_daily_report(test_stocks)
    
    # 测试宏观经济报告
    print("\n3. 测试宏观经济报告:")
    test_macro = {
        'level': 'low',
        'message': '当前宏观环境整体稳定，资金面充裕，通胀水平温和',
        'alerts': []
    }
    notifier.send_macro_alert(test_macro)
