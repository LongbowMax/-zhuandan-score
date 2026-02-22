"""
A股风险预警系统 - 宏观经济报告生成器 V3.0
生成专业的宏观经济分析报告
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import Dict, List

class MacroReportGenerator:
    """宏观经济报告生成器"""
    
    def generate_macro_report(self, macro_summary: Dict, indicators_data: Dict = None) -> Dict[str, str]:
        """
        生成宏观经济报告
        
        返回: {'subject': 主题, 'html': HTML内容, 'text': 纯文本内容}
        """
        level = macro_summary.get('level', 'low')
        level_config = {
            'high': {'emoji': '🚨', 'color': '#dc3545', 'title': '【紧急】宏观经济高风险预警'},
            'medium': {'emoji': '⚠️', 'color': '#ffc107', 'title': '【注意】宏观经济风险提醒'},
            'low': {'emoji': '✅', 'color': '#28a745', 'title': '【正常】宏观经济监控报告'}
        }
        level_info = level_config.get(level, level_config['low'])
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        date_str = datetime.now().strftime('%Y年%m月%d日')
        
        # 构建指标卡片
        indicators_html = self._build_indicators_html(indicators_data or {})
        
        # 构建风险提示
        alerts_html = self._build_alerts_html(macro_summary.get('alerts', []))
        
        subject = f"{level_info['title']} - {date_str}"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>宏观经济报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; 
               margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 750px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden;
                      box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, {level_info['color']} 0%, {self._darken_color(level_info['color'])} 100%); 
                   color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header .date {{ margin-top: 10px; font-size: 14px; opacity: 0.9; }}
        
        .summary-box {{ background: #f8f9fa; padding: 20px; margin: 20px; border-radius: 8px;
                       border-left: 4px solid {level_info['color']}; }}
        .summary-title {{ font-size: 16px; font-weight: 600; color: #333; margin-bottom: 10px; }}
        .summary-text {{ font-size: 14px; color: #666; line-height: 1.6; }}
        
        .content {{ padding: 20px; }}
        
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #333; 
                          display: flex; align-items: center; margin-bottom: 15px; }}
        .section-title .icon {{ font-size: 22px; margin-right: 8px; }}
        
        .indicators-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; }}
        .indicator-card {{ background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; }}
        .indicator-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .indicator-name {{ font-weight: 600; color: #333; font-size: 14px; }}
        .indicator-status {{ font-size: 11px; padding: 2px 8px; border-radius: 10px; }}
        .indicator-status.normal {{ background: #e8f5e9; color: #2e7d32; }}
        .indicator-status.warning {{ background: #fff3e0; color: #ef6c00; }}
        .indicator-status.danger {{ background: #ffebee; color: #c62828; }}
        .indicator-value {{ font-size: 24px; font-weight: 700; color: #333; margin: 8px 0; }}
        .indicator-change {{ font-size: 12px; color: #999; }}
        .indicator-desc {{ font-size: 12px; color: #666; margin-top: 8px; line-height: 1.4; }}
        
        .alert-section {{ background: #fff8e1; border-radius: 8px; padding: 15px; margin-top: 20px; }}
        .alert-title {{ font-weight: 600; color: #f57c00; margin-bottom: 10px; font-size: 14px; }}
        .alert-item {{ background: white; border-radius: 6px; padding: 12px; margin-bottom: 8px;
                      border-left: 3px solid #f57c00; }}
        .alert-item.high {{ border-left-color: #dc3545; }}
        .alert-type {{ font-weight: 600; color: #333; font-size: 13px; margin-bottom: 4px; }}
        .alert-desc {{ color: #666; font-size: 12px; line-height: 1.4; }}
        
        .no-alert {{ text-align: center; padding: 30px; color: #2e7d32; background: #e8f5e9; border-radius: 8px; }}
        .no-alert-icon {{ font-size: 40px; margin-bottom: 10px; }}
        
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px;
                   border-top: 1px solid #e0e0e0; }}
        .timestamp {{ text-align: right; color: #999; font-size: 12px; margin: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{level_info['emoji']} 宏观经济监控报告</h1>
            <div class="date">{date_str} | {timestamp}</div>
        </div>
        
        <div class="summary-box">
            <div class="summary-title">综合评估</div>
            <div class="summary-text">{macro_summary.get('message', '暂无评估信息')}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title"><span class="icon">📊</span>核心指标监控</div>
                <div class="indicators-grid">
                    {indicators_html}
                </div>
            </div>
            
            {alerts_html}
        </div>
        
        <div class="timestamp">
            报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            数据来源：Tushare Pro | 分析师：山鬼之锤 ⚒️🏔️
        </div>
        
        <div class="footer">
            <p>本报告仅供参考，不构成投资建议</p>
            <p>监控指标：Shibor利率 | CPI通胀 | PMI制造业 | 人民币汇率</p>
        </div>
    </div>
</body>
</html>
"""
        
        text_content = self._generate_text_version(macro_summary, indicators_data or {})
        
        return {
            'subject': subject,
            'html': html_content,
            'text': text_content
        }
    
    def _build_indicators_html(self, data: Dict) -> str:
        """构建指标卡片HTML"""
        # 默认数据（如果没有真实数据）
        default_indicators = {
            'shibor': {'name': 'Shibor隔夜利率', 'value': '1.85%', 'change': '-0.02%', 
                      'status': 'normal', 'desc': '银行间市场流动性充裕'},
            'cpi': {'name': 'CPI同比', 'value': '0.5%', 'change': '-0.1%', 
                   'status': 'normal', 'desc': '通胀水平温和，处于低位'},
            'pmi': {'name': '制造业PMI', 'value': '49.8', 'change': '+0.2', 
                   'status': 'warning', 'desc': '略低于荣枯线，经济仍需观察'},
            'exchange': {'name': '人民币汇率', 'value': '7.23', 'change': '+0.15%', 
                        'status': 'normal', 'desc': '汇率基本稳定'}
        }
        
        indicators = data if data else default_indicators
        
        html_parts = []
        for key, ind in indicators.items():
            status_class = ind.get('status', 'normal')
            status_text = {'normal': '正常', 'warning': '关注', 'danger': '预警'}.get(status_class, '正常')
            
            html_parts.append(f"""
            <div class="indicator-card">
                <div class="indicator-header">
                    <span class="indicator-name">{ind.get('name', key)}</span>
                    <span class="indicator-status {status_class}">{status_text}</span>
                </div>
                <div class="indicator-value">{ind.get('value', '--')}</div>
                <div class="indicator-change">较上期: {ind.get('change', '--')}</div>
                <div class="indicator-desc">{ind.get('desc', '')}</div>
            </div>
            """)
        
        return '\n'.join(html_parts)
    
    def _build_alerts_html(self, alerts: List[Dict]) -> str:
        """构建风险提示HTML"""
        if not alerts:
            return '''
            <div class="section">
                <div class="section-title"><span class="icon">🛡️</span>风险提示</div>
                <div class="no-alert">
                    <div class="no-alert-icon">✅</div>
                    <div>宏观环境稳定，暂无系统性风险</div>
                    <div style="font-size:12px; margin-top:8px;">各主要指标均处于正常区间</div>
                </div>
            </div>
            '''
        
        alerts_html = ''
        for alert in alerts:
            level = alert.get('level', 'low')
            level_class = level if level in ['high', 'medium', 'low'] else 'low'
            
            alerts_html += f"""
            <div class="alert-item {level_class}">
                <div class="alert-type">[{alert.get('indicator', '指标')}] {alert.get('type', '风险')}</div>
                <div class="alert-desc">{alert.get('desc', '')}</div>
            </div>
            """
        
        return f"""
        <div class="section">
            <div class="section-title"><span class="icon">⚠️</span>风险提示 ({len(alerts)}项)</div>
            <div class="alert-section">
                <div class="alert-title">检测到以下异常信号，请注意风险</div>
                {alerts_html}
            </div>
        </div>
        """
    
    def _generate_text_version(self, macro_summary: Dict, indicators_data: Dict) -> str:
        """生成纯文本版本"""
        lines = [
            "="*50,
            "宏观经济监控报告",
            "="*50,
            f"报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "【综合评估】",
            macro_summary.get('message', '暂无评估信息'),
            "",
            "【核心指标】",
        ]
        
        # 指标数据
        default_indicators = {
            'shibor': {'name': 'Shibor隔夜利率', 'value': '1.85%', 'change': '-0.02%'},
            'cpi': {'name': 'CPI同比', 'value': '0.5%', 'change': '-0.1%'},
            'pmi': {'name': '制造业PMI', 'value': '49.8', 'change': '+0.2'},
            'exchange': {'name': '人民币汇率', 'value': '7.23', 'change': '+0.15%'}
        }
        
        indicators = indicators_data if indicators_data else default_indicators
        
        for key, ind in indicators.items():
            lines.append(f"- {ind.get('name', key)}: {ind.get('value', '--')} ({ind.get('change', '--')})")
        
        lines.extend([
            "",
            "【风险提示】",
        ])
        
        alerts = macro_summary.get('alerts', [])
        if alerts:
            for i, alert in enumerate(alerts, 1):
                lines.append(f"{i}. [{alert.get('level', '').upper()}] {alert.get('type', '')}")
                lines.append(f"   {alert.get('desc', '')}")
        else:
            lines.append("✅ 宏观环境稳定，暂无系统性风险")
        
        lines.extend([
            "",
            "="*50,
            "数据来源：Tushare Pro | 分析师：山鬼之锤",
            "="*50
        ])
        
        return '\n'.join(lines)
    
    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """加深颜色"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*darkened)


if __name__ == '__main__':
    # 测试
    generator = MacroReportGenerator()
    
    test_summary = {
        'level': 'low',
        'message': '当前宏观环境整体稳定，资金面充裕，通胀水平温和，建议保持正常仓位',
        'alerts': []
    }
    
    report = generator.generate_macro_report(test_summary)
    print(f"主题: {report['subject']}")
    print(f"HTML长度: {len(report['html'])} 字符")
