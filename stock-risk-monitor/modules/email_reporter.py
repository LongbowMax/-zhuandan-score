"""
A股风险预警系统 - 邮件报告模块 V3.0
支持HTML可视化报告生成
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class EmailReporter:
    """邮件报告生成器"""
    
    def __init__(self, config_path='../config/settings.json'):
        self.config = self._load_config(config_path)
        self.email_config = self.config.get('notification', {}).get('email', {})
        
    def _load_config(self, path):
        """加载配置"""
        # 支持相对路径和绝对路径
        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.path.join(os.path.dirname(__file__), path)
        
        # 如果文件不存在，尝试从工作目录找
        if not os.path.exists(full_path):
            workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            alt_paths = [
                os.path.join(workspace, 'config', 'settings.json'),
                os.path.join(workspace, '..', 'config', 'settings.json'),
                os.path.join(os.getcwd(), 'config', 'settings.json'),
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    full_path = alt_path
                    break
        
        if not os.path.exists(full_path):
            # 返回默认配置
            return {"watchlist": [], "notification": {"email": {"enabled": True}}}
        
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_risk_alert_email(self, stock_name: str, stock_code: str, 
                                   risk_summary: Dict, all_risks: List[Dict],
                                   daily_data: Optional[Dict] = None) -> Dict[str, str]:
        """
        生成风险预警邮件
        
        返回: {'subject': 主题, 'html': HTML内容, 'text': 纯文本内容}
        """
        level = risk_summary.get('level', 'low')
        level_config = {
            'high': {'emoji': '', 'color': '#dc3545', 'title': '【紧急】高风险预警'},
            'medium': {'emoji': '⚠️', 'color': '#ffc107', 'title': '【注意】风险提醒'},
            'low': {'emoji': '✓', 'color': '#28a745', 'title': '【正常】每日监控'}
        }
        
        level_info = level_config.get(level, level_config['low'])
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 构建风险项HTML
        risks_html = self._build_risks_html(all_risks)
        
        # 构建数据摘要HTML
        data_summary_html = ""
        if daily_data:
            data_summary_html = self._build_data_summary_html(daily_data)
        
        subject = f"{level_info['title']} - {stock_name}({stock_code})"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>股票风险预警</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; 
               margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden;
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, {level_info['color']} 0%, {self._darken_color(level_info['color'])} 100%); 
                   color: white; padding: 25px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
        .header .stock-info {{ margin-top: 10px; font-size: 16px; opacity: 0.9; }}
        .content {{ padding: 25px; }}
        .section {{ margin-bottom: 25px; }}
        .section-title {{ font-size: 16px; font-weight: 600; color: #333; 
                          border-left: 4px solid {level_info['color']}; padding-left: 10px; margin-bottom: 15px; }}
        .summary-box {{ background: #f8f9fa; border-radius: 6px; padding: 15px; margin-bottom: 20px; }}
        .summary-text {{ font-size: 15px; color: #333; line-height: 1.6; }}
        .risk-item {{ background: white; border: 1px solid #e0e0e0; border-radius: 6px; padding: 12px; 
                      margin-bottom: 10px; border-left: 4px solid #dc3545; }}
        .risk-item.medium {{ border-left-color: #ffc107; }}
        .risk-item.low {{ border-left-color: #17a2b8; }}
        .risk-type {{ font-weight: 600; color: #333; margin-bottom: 5px; }}
        .risk-desc {{ color: #666; font-size: 14px; line-height: 1.5; }}
        .risk-level {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; 
                       font-weight: 500; margin-left: 8px; }}
        .risk-level.high {{ background: #ffe5e5; color: #dc3545; }}
        .risk-level.medium {{ background: #fff3e0; color: #f57c00; }}
        .risk-level.low {{ background: #e3f2fd; color: #1976d2; }}
        .data-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 15px; }}
        .data-item {{ text-align: center; padding: 12px; background: #f8f9fa; border-radius: 6px; }}
        .data-label {{ font-size: 12px; color: #666; margin-bottom: 4px; }}
        .data-value {{ font-size: 18px; font-weight: 600; color: #333; }}
        .data-value.up {{ color: #dc3545; }}
        .data-value.down {{ color: #28a745; }}
        .footer {{ background: #f8f9fa; padding: 15px 25px; text-align: center; color: #999; font-size: 12px; }}
        .timestamp {{ text-align: right; color: #999; font-size: 12px; margin-top: 20px; }}
        .no-risk {{ text-align: center; padding: 30px; color: #28a745; }}
        .no-risk-icon {{ font-size: 48px; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{level_info['emoji']} 股票风险预警</h1>
            <div class="stock-info">{stock_name} ({stock_code}) | {timestamp}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">评估摘要</div>
                <div class="summary-box">
                    <div class="summary-text">
                        <strong>风险等级：</strong><span style="color: {level_info['color']}; font-size: 18px;">
                        {level.upper()}</span><br>
                        <strong>评估结论：</strong>{risk_summary.get('message', '暂无评估信息')}
                    </div>
                </div>
            </div>
            
            {data_summary_html}
            
            <div class="section">
                <div class="section-title">风险详情 ({len(all_risks)}项)</div>
                {risks_html}
            </div>
            
            <div class="timestamp">
                报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                数据来源：Tushare Pro | 分析师：山鬼之锤 ⚒️🏔️
            </div>
        </div>
        
        <div class="footer">
            本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。
        </div>
    </div>
</body>
</html>
"""
        
        # 纯文本版本
        text_content = self._generate_text_version(stock_name, stock_code, risk_summary, all_risks)
        
        return {
            'subject': subject,
            'html': html_content,
            'text': text_content
        }
    
    def generate_daily_report_email(self, report_date: datetime, 
                                     stocks_data: List[Dict]) -> Dict[str, str]:
        """
        生成每日监控报告邮件
        
        stocks_data: 各股票的分析结果列表
        """
        date_str = report_date.strftime('%Y-%m-%d')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][report_date.weekday()]
        
        # 统计信息
        total_stocks = len(stocks_data)
        high_risk = len([s for s in stocks_data if s.get('risk_level') == 'high'])
        medium_risk = len([s for s in stocks_data if s.get('risk_level') == 'medium'])
        
        # 持仓盈亏计算
        position_stocks = [s for s in stocks_data if s.get('position', 0) > 0]
        
        # 构建股票列表HTML
        stocks_html = self._build_daily_stocks_html(stocks_data)
        
        subject = f"[日报] {date_str} {weekday} 股票监控报告"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日股票监控报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; 
               margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden;
                      box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 26px; font-weight: 600; }}
        .header .date {{ margin-top: 10px; font-size: 16px; opacity: 0.9; }}
        
        .summary-bar {{ display: flex; background: #f8f9fa; padding: 20px; border-bottom: 1px solid #e0e0e0; }}
        .summary-item {{ flex: 1; text-align: center; padding: 10px; }}
        .summary-value {{ font-size: 28px; font-weight: 700; color: #333; }}
        .summary-label {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .summary-value.danger {{ color: #dc3545; }}
        .summary-value.warning {{ color: #ffc107; }}
        .summary-value.safe {{ color: #28a745; }}
        
        .content {{ padding: 25px; }}
        .section {{ margin-bottom: 30px; }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #333; 
                          border-left: 4px solid #667eea; padding-left: 12px; margin-bottom: 20px; 
                          display: flex; align-items: center; }}
        .section-title .icon {{ margin-right: 8px; font-size: 20px; }}
        
        .stock-card {{ background: white; border: 1px solid #e0e0e0; border-radius: 8px; 
                      margin-bottom: 15px; overflow: hidden; }}
        .stock-header {{ display: flex; justify-content: space-between; align-items: center;
                         padding: 15px 20px; background: #fafafa; border-bottom: 1px solid #e0e0e0; }}
        .stock-name {{ font-size: 16px; font-weight: 600; color: #333; }}
        .stock-code {{ color: #999; font-size: 14px; margin-left: 8px; }}
        .stock-badge {{ padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }}
        .stock-badge.high {{ background: #ffe5e5; color: #dc3545; }}
        .stock-badge.medium {{ background: #fff3e0; color: #f57c00; }}
        .stock-badge.low {{ background: #e8f5e9; color: #2e7d32; }}
        
        .stock-body {{ padding: 15px 20px; }}
        .stock-metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 15px; }}
        .metric {{ text-align: center; }}
        .metric-value {{ font-size: 16px; font-weight: 600; color: #333; }}
        .metric-value.up {{ color: #dc3545; }}
        .metric-value.down {{ color: #28a745; }}
        .metric-label {{ font-size: 11px; color: #999; margin-top: 3px; }}
        
        .risk-list {{ margin-top: 10px; }}
        .risk-tag {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 11px;
                     margin-right: 6px; margin-bottom: 6px; }}
        .risk-tag.high {{ background: #ffe5e5; color: #c62828; }}
        .risk-tag.medium {{ background: #fff3e0; color: #ef6c00; }}
        .risk-tag.low {{ background: #e3f2fd; color: #1565c0; }}
        
        .no-risk {{ text-align: center; padding: 40px; color: #28a745; background: #f8f9fa; border-radius: 8px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px;
                   border-top: 1px solid #e0e0e0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 每日股票监控报告</h1>
            <div class="date">{date_str} {weekday}</div>
        </div>
        
        <div class="summary-bar">
            <div class="summary-item">
                <div class="summary-value">{total_stocks}</div>
                <div class="summary-label">监控股票</div>
            </div>
            <div class="summary-item">
                <div class="summary-value danger">{high_risk}</div>
                <div class="summary-label">高风险</div>
            </div>
            <div class="summary-item">
                <div class="summary-value warning">{medium_risk}</div>
                <div class="summary-label">中风险</div>
            </div>
            <div class="summary-item">
                <div class="summary-value safe">{total_stocks - high_risk - medium_risk}</div>
                <div class="summary-label">正常</div>
            </div>
        </div>
        
        <div class="content">
            {self._build_position_section(position_stocks) if position_stocks else ''}
            
            <div class="section">
                <div class="section-title"><span class="icon">📈</span>个股监控详情</div>
                {stocks_html}
            </div>
        </div>
        
        <div class="footer">
            <p>数据来源：Tushare Pro | 分析师：山鬼之锤 ⚒️🏔️</p>
            <p>本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。</p>
        </div>
    </div>
</body>
</html>
"""
        
        text_content = f"每日股票监控报告 - {date_str} {weekday}\n\n"
        text_content += f"监控股票：{total_stocks}只 | 高风险：{high_risk} | 中风险：{medium_risk}\n\n"
        
        return {
            'subject': subject,
            'html': html_content,
            'text': text_content
        }
    
    def _build_risks_html(self, risks: List[Dict]) -> str:
        """构建风险项HTML"""
        if not risks:
            return '''
            <div class="no-risk">
                <div class="no-risk-icon">✓</div>
                <div>未发现明显风险项，当前状态良好</div>
            </div>
            '''
        
        html_parts = []
        for risk in risks:
            level = risk.get('level', 'low')
            level_class = level if level in ['high', 'medium', 'low'] else 'low'
            level_text = {'high': '高', 'medium': '中', 'low': '低'}.get(level, '低')
            
            html_parts.append(f"""
            <div class="risk-item {level_class}">
                <div class="risk-type">
                    {risk.get('type', '未知风险')}
                    <span class="risk-level {level_class}">{level_text}风险</span>
                </div>
                <div class="risk-desc">{risk.get('desc', '')}</div>
            </div>
            """)
        
        return '\n'.join(html_parts)
    
    def _build_data_summary_html(self, data: Dict) -> str:
        """构建数据摘要HTML"""
        if not data:
            return ""
        
        change_pct = data.get('change_pct', 0)
        change_class = 'up' if change_pct > 0 else 'down' if change_pct < 0 else ''
        change_sign = '+' if change_pct > 0 else ''
        
        return f"""
        <div class="section">
            <div class="section-title">行情数据</div>
            <div class="data-grid">
                <div class="data-item">
                    <div class="data-label">最新价</div>
                    <div class="data-value {change_class}">{data.get('close', '--')}</div>
                </div>
                <div class="data-item">
                    <div class="data-label">涨跌幅</div>
                    <div class="data-value {change_class}">{change_sign}{change_pct:.2f}%</div>
                </div>
                <div class="data-item">
                    <div class="data-label">成交量</div>
                    <div class="data-value">{data.get('volume', '--')}</div>
                </div>
            </div>
        </div>
        """
    
    def _build_daily_stocks_html(self, stocks_data: List[Dict]) -> str:
        """构建日报股票列表HTML"""
        if not stocks_data:
            return '<div class="no-risk">暂无监控股票</div>'
        
        html_parts = []
        for stock in stocks_data:
            level = stock.get('risk_level', 'low')
            badge_class = level if level in ['high', 'medium', 'low'] else 'low'
            badge_text = {'high': '高风险', 'medium': '中风险', 'low': '正常'}.get(level, '正常')
            
            # 涨跌幅颜色
            change_pct = stock.get('change_pct', 0)
            change_class = 'up' if change_pct > 0 else 'down' if change_pct < 0 else ''
            change_sign = '+' if change_pct > 0 else ''
            
            # 持仓标识
            position_badge = ""
            if stock.get('position', 0) > 0:
                position_badge = f"<span style='color:#667eea; margin-left:8px;'>[持仓 {stock.get('position',0)*100:.0f}%]</span>"
            
            # 风险标签
            risk_tags = ""
            risks = stock.get('risks', [])
            if risks:
                tags = [f"<span class='risk-tag {r.get('level', 'low')}'>{r.get('type', '风险')}</span>" 
                        for r in risks[:3]]
                risk_tags = '<div class="risk-list">' + ''.join(tags) + '</div>'
            
            html_parts.append(f"""
            <div class="stock-card">
                <div class="stock-header">
                    <div>
                        <span class="stock-name">{stock.get('name', '未知')}</span>
                        <span class="stock-code">({stock.get('code', '--')})</span>
                        {position_badge}
                    </div>
                    <span class="stock-badge {badge_class}">{badge_text}</span>
                </div>
                <div class="stock-body">
                    <div class="stock-metrics">
                        <div class="metric">
                            <div class="metric-value {change_class}">{change_sign}{change_pct:.2f}%</div>
                            <div class="metric-label">今日涨跌</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{stock.get('close', '--')}</div>
                            <div class="metric-label">最新价</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{stock.get('volume', '--')}</div>
                            <div class="metric-label">成交量</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{stock.get('risk_count', 0)}</div>
                            <div class="metric-label">风险项</div>
                        </div>
                    </div>
                    {risk_tags}
                </div>
            </div>
            """)
        
        return '\n'.join(html_parts)
    
    def _build_position_section(self, position_stocks: List[Dict]) -> str:
        """构建持仓部分HTML"""
        # 简化的持仓显示，盈亏计算需要在后续版本中完善
        stocks_html = ""
        for stock in position_stocks:
            stocks_html += f"<div style='margin-bottom:10px; padding:10px; background:#f8f9fa; border-radius:6px;'>"
            stocks_html += f"<strong>{stock.get('name')}</strong> ({stock.get('code')}) - 仓位 {stock.get('position',0)*100:.0f}%"
            stocks_html += f"<br><small style='color:#666;'>今日涨跌: {stock.get('change_pct', 0):.2f}%</small>"
            stocks_html += "</div>"
        
        return f"""
        <div class="section">
            <div class="section-title"><span class="icon">💰</span>持仓概览</div>
            {stocks_html}
        </div>
        """
    
    def _generate_text_version(self, stock_name: str, stock_code: str, 
                               risk_summary: Dict, all_risks: List[Dict]) -> str:
        """生成纯文本版本（用于邮件客户端不支持HTML时）"""
        level = risk_summary.get('level', 'low')
        level_emoji = {'high': '!!', 'medium': '! ', 'low': 'OK'}.get(level, '--')
        
        lines = [
            f"[{level_emoji}] 股票风险预警: {stock_name} ({stock_code})",
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"风险等级: {level.upper()}",
            f"评估结果: {risk_summary.get('message', '')}",
            "",
            f"风险详情 ({len(all_risks)}项):"
        ]
        
        if all_risks:
            for i, risk in enumerate(all_risks, 1):
                risk_level = risk.get('level', 'low')
                risk_emoji = {'high': '!!', 'medium': '! ', 'low': '-'}.get(risk_level, '--')
                lines.append(f"{i}. [{risk_emoji}] {risk.get('type', '')}")
                lines.append(f"   {risk.get('desc', '')}")
        else:
            lines.append("未发现明显风险项")
        
        lines.append("")
        lines.append("—— 山鬼之锤")
        
        return '\n'.join(lines)
    
    def _darken_color(self, hex_color: str, factor: float = 0.8) -> str:
        """加深颜色（用于渐变）"""
        # 简单的颜色加深逻辑
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * factor) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*darkened)


if __name__ == '__main__':
    # 测试
    reporter = EmailReporter()
    
    # 测试风险预警邮件
    test_risks = [
        {'level': 'high', 'type': '净利润大幅下滑', 'desc': '净利润同比下降35%，超过预警阈值'},
        {'level': 'medium', 'type': '营收增速放缓', 'desc': '营收同比增长仅2.5%，低于行业平均'}
    ]
    test_summary = {
        'level': 'high',
        'message': '发现2项高风险，建议减仓观望',
        'risks': test_risks
    }
    
    email = reporter.generate_risk_alert_email("南网储能", "600995", test_summary, test_risks)
    print(f"主题: {email['subject']}")
    print(f"HTML长度: {len(email['html'])} 字符")
