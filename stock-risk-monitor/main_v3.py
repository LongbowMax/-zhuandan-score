"""
A股风险预警系统 - 主程序 V3.0
支持：多股票监控 + 宏观经济监控 + 邮件报告系统
"""
import sys
import os

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher import DataFetcher
from modules.fundamental_check import FundamentalAnalyzer
from modules.technical_analyzer import TechnicalAnalyzer
from modules.macro_monitor import MacroMonitor
from modules.email_notifier import EmailNotifier
import json
from datetime import datetime

def load_config():
    """加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), '../config/settings.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_stock(stock_config, fetcher, email_notifier, config):
    """分析单只股票"""
    code = stock_config['code']
    name = stock_config['name']
    ts_code = f"{code}.SH" if code.startswith('6') else f"{code}.SZ"
    position = stock_config.get('position_ratio', 0)
    
    print(f"\n{'='*60}")
    print(f"  股票: {name} ({code})")
    if position > 0:
        print(f"  持仓: {position*100:.0f}% {'[重仓]' if position > 0.5 else ''}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    
    all_risks = []
    daily_data = {}
    
    # 1. 行情数据
    print("\n  [行情数据]")
    try:
        daily_df = fetcher.get_daily_data(ts_code, days=60)
        if daily_df is not None and not daily_df.empty:
            latest = daily_df.iloc[-1]
            daily_data = {
                'close': latest.get('close', 0),
                'change_pct': latest.get('pct_chg', 0),
                'volume': f"{latest.get('vol', 0)/10000:.1f}万手"
            }
            print(f"    最新价: {daily_data['close']:.2f}")
            print(f"    涨跌幅: {daily_data['change_pct']:.2f}%")
    except Exception as e:
        print(f"    获取行情数据失败: {e}")
    
    # 2. 技术面分析
    print("  [技术分析]")
    try:
        tech_analyzer = TechnicalAnalyzer(stock_config)
        tech_risks = tech_analyzer.analyze(daily_df)
        all_risks.extend(tech_risks)
        print(f"    {'异常: ' + str(len(tech_risks)) + '项' if tech_risks else '正常'}")
    except Exception as e:
        print(f"    技术分析失败: {e}")
    
    # 3. 基本面分析
    print("  [基本面分析]")
    try:
        fin_df = fetcher.get_financial_data(ts_code)
        fund_analyzer = FundamentalAnalyzer()
        fund_risks = fund_analyzer.analyze_financial_data(fin_df)
        all_risks.extend(fund_risks)
        print(f"    {'异常: ' + str(len(fund_risks)) + '项' if fund_risks else '正常'}")
        
        # 业绩快报/预告
        express_df = fetcher.get_express_data(ts_code)
        express_risks = fund_analyzer.analyze_express_report(express_df)
        all_risks.extend(express_risks)
        
        forecast_df = fetcher.get_forecast_data(ts_code)
        forecast_risks = fund_analyzer.analyze_forecast(forecast_df)
        all_risks.extend(forecast_risks)
        
        if express_risks or forecast_risks:
            print(f"    业绩预警: {len(express_risks) + len(forecast_risks)}项")
    except Exception as e:
        print(f"    基本面分析失败: {e}")
    
    # 4. 汇总风险
    fund_summary = fund_analyzer.get_summary() if 'fund_analyzer' in locals() else {'status': 'unknown', 'level': 'low', 'message': '分析未完成'}
    risk_summary = {
        'status': fund_summary['status'],
        'level': fund_summary['level'],
        'message': fund_summary['message'],
        'count': len(all_risks),
        'risks': all_risks
    }
    
    # 技术面高风险升级
    high_tech_risks = [r for r in tech_risks if r.get('level') == 'high'] if 'tech_risks' in locals() else []
    if high_tech_risks and risk_summary['level'] != 'high':
        risk_summary['level'] = 'high'
        risk_summary['status'] = 'danger'
        risk_summary['message'] += '，技术面出现高风险信号'
    
    # 5. 判断是否发送预警邮件
    should_alert = email_notifier.should_send_alert(risk_summary['level'])
    
    if should_alert:
        print(f"\n  [邮件] 发送风险预警...")
        email_notifier.send_risk_alert(name, code, risk_summary, all_risks, daily_data)
    
    # 6. 保存报告
    save_report(name, code, risk_summary, all_risks)
    
    print(f"\n  结果: {risk_summary['message']}")
    
    return {
        'code': code,
        'name': name,
        'position': position,
        'risk_level': risk_summary['level'],
        'risk_count': len(all_risks),
        'change_pct': daily_data.get('change_pct', 0),
        'close': daily_data.get('close', 0),
        'volume': daily_data.get('volume', '--'),
        'risks': all_risks
    }

def analyze_macro(fetcher, email_notifier, config):
    """宏观经济分析 - 单独发送报告"""
    print("\n" + "="*60)
    print("  宏观经济监控")
    print("="*60)
    
    try:
        macro = MacroMonitor(fetcher.pro)
        macro.check_all()
        summary = macro.get_summary()
        
        # 始终发送宏观经济报告（作为单独报告）
        print("\n  [邮件] 发送宏观经济报告...")
        email_notifier.send_macro_alert(summary)
        
        return summary
    except Exception as e:
        print(f"  宏观经济分析失败: {e}")
        return {'level': 'low', 'message': '分析失败', 'alerts': []}

def save_report(stock_name, stock_code, summary, risks):
    """保存分析报告"""
    report_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{stock_code}_{date_str}_report.txt"
    filepath = os.path.join(report_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"风险分析报告 - {stock_name} ({stock_code})\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"风险等级: {summary['level'].upper()}\n")
        f.write(f"评估结论: {summary['message']}\n")
        f.write("\n" + "="*50 + "\n\n")
        
        if risks:
            f.write("详细风险项:\n")
            for i, risk in enumerate(risks, 1):
                f.write(f"{i}. [{risk.get('level', 'unknown').upper()}] {risk.get('type', '')}\n")
                f.write(f"   {risk.get('desc', '')}\n\n")
        else:
            f.write("未发现明显风险项\n")

def send_daily_summary(all_results, email_notifier):
    """发送每日汇总报告"""
    print("\n" + "="*60)
    print("  发送每日监控报告")
    print("="*60)
    
    try:
        email_notifier.send_daily_report(all_results)
    except Exception as e:
        print(f"  发送日报失败: {e}")

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  A股风险预警系统 v3.0")
    print("  支持邮件报告 + 5只股票监控")
    print("="*60)
    
    # 加载配置
    try:
        config = load_config()
        print("\n[配置] 加载成功")
        print(f"       版本: {config.get('version', 'unknown')}")
        print(f"       监控股票: {len(config.get('watchlist', []))}只")
        
        # 检查邮件配置
        email_enabled = config.get('notification', {}).get('email', {}).get('enabled', False)
        if email_enabled:
            print("[通知] 邮件推送已启用")
        else:
            print("[通知] 邮件推送未启用")
            
    except Exception as e:
        print(f"[错误] 加载配置失败: {e}")
        return
    
    # 初始化
    try:
        fetcher = DataFetcher()
        print("[数据] 接口连接成功")
    except Exception as e:
        print(f"[错误] 数据接口连接失败: {e}")
        return
    
    email_notifier = EmailNotifier()
    
    # 获取监控列表
    watchlist = config.get('watchlist', [])
    
    if not watchlist:
        print("[警告] 监控列表为空")
        return
    
    print(f"\n[监控] 股票数量: {len(watchlist)}")
    for stock in watchlist:
        pos = f" [持仓 {stock.get('position_ratio',0)*100:.0f}%]" if stock.get('position_ratio',0) > 0 else ""
        print(f"       - {stock['name']} ({stock['code']}){pos}")
    
    # 1. 宏观经济检查
    if config.get('macro_monitor', {}).get('enabled', True):
        print("\n" + "="*60)
        print("  宏观经济检查")
        print("="*60)
        macro_summary = analyze_macro(fetcher, email_notifier, config)
    
    # 2. 个股检查
    print("\n" + "="*60)
    print("  个股风险检查")
    print("="*60)
    
    results = []
    for stock in watchlist:
        try:
            result = analyze_stock(stock, fetcher, email_notifier, config)
            results.append(result)
        except Exception as e:
            print(f"[错误] 分析 {stock['name']} 时出错: {e}")
    
    # 3. 发送日报
    send_daily_summary(results, email_notifier)
    
    # 4. 汇总
    print("\n" + "="*60)
    print("  本次监控汇总")
    print("="*60)
    
    for r in results:
        emoji = {'high': '!!', 'medium': '! ', 'low': 'OK', 'safe': 'OK'}.get(r['risk_level'], '--')
        pos_info = f"[{r['position']*100:.0f}%]" if r['position'] > 0 else "[观望]"
        change_emoji = "↑" if r.get('change_pct', 0) > 0 else "↓" if r.get('change_pct', 0) < 0 else "→"
        print(f"  [{emoji}] {r['name']} ({r['code']}) {pos_info} - {r['risk_level'].upper()} {change_emoji} {r.get('change_pct', 0):.2f}%")
    
    # 持仓集中度提醒
    total_position = sum(r['position'] for r in results)
    if total_position > 0.8:
        print(f"\n  [注意] 总持仓 {total_position*100:.0f}%，集中度较高，建议适当分散")
    
    print("\n" + "="*60)
    print("  检查完成")
    print("  报告已发送至: longbow_max@163.com")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
