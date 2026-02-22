"""
A股风险预警系统 - 主程序 V2.0
支持多股票监控 + 宏观经济监控 + 微信通知
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
from modules.notifier import Notifier
from modules.macro_monitor import MacroMonitor
import json
from datetime import datetime

def load_config():
    """加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), '../config/settings.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_stock(stock_config, fetcher, notifier, config):
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
    
    # 1. 行情数据
    print("\n  [行情数据]")
    daily_df = fetcher.get_daily_data(ts_code, days=60)
    
    # 2. 技术面分析
    print("  [技术分析]")
    tech_analyzer = TechnicalAnalyzer(stock_config)
    tech_risks = tech_analyzer.analyze(daily_df)
    all_risks.extend(tech_risks)
    print(f"    {'异常: ' + str(len(tech_risks)) + '项' if tech_risks else '正常'}")
    
    # 3. 基本面分析
    print("  [基本面分析]")
    fin_df = fetcher.get_financial_data(ts_code)
    fund_analyzer = FundamentalAnalyzer()
    fund_risks = fund_analyzer.analyze_financial_data(fin_df)
    all_risks.extend(fund_risks)
    print(f"    {'异常: ' + str(len(fund_risks)) + '项' if fund_risks else '正常'}")
    
    # 4. 业绩快报/预告
    express_df = fetcher.get_express_data(ts_code)
    express_risks = fund_analyzer.analyze_express_report(express_df)
    all_risks.extend(express_risks)
    
    forecast_df = fetcher.get_forecast_data(ts_code)
    forecast_risks = fund_analyzer.analyze_forecast(forecast_df)
    all_risks.extend(forecast_risks)
    
    if express_risks or forecast_risks:
        print(f"    业绩预警: {len(express_risks) + len(forecast_risks)}项")
    
    # 5. 汇总风险
    fund_summary = fund_analyzer.get_summary()
    risk_summary = {
        'status': fund_summary['status'],
        'level': fund_summary['level'],
        'message': fund_summary['message'],
        'count': len(all_risks),
        'risks': all_risks
    }
    
    # 技术面高风险升级
    high_tech_risks = [r for r in tech_risks if r.get('level') == 'high']
    if high_tech_risks and risk_summary['level'] != 'high':
        risk_summary['level'] = 'high'
        risk_summary['status'] = 'danger'
        risk_summary['message'] += '，技术面出现高风险信号'
    
    # 持仓建议
    advice = tech_analyzer.get_position_advice(daily_df, stock_config.get('cost_price'))
    if advice:
        print(f"  [建议] {advice}")
    
    # 发送通知（仅对有持仓或高风险的股票）
    if position > 0 or risk_summary['level'] in ['high', 'medium']:
        notifier.send_alert(name, code, risk_summary, config)
    
    # 保存报告
    save_report(name, code, risk_summary, all_risks)
    
    print(f"\n  结果: {risk_summary['message']}")
    
    return {
        'code': code,
        'name': name,
        'position': position,
        'risk_level': risk_summary['level'],
        'risk_count': len(all_risks)
    }

def analyze_macro(fetcher, notifier, config):
    """宏观经济分析"""
    print("\n" + "="*60)
    print("  宏观经济监控")
    print("="*60)
    
    macro = MacroMonitor(fetcher.pro)
    macro.check_all()
    summary = macro.get_summary()
    
    # 发送宏观预警（如果有风险）
    if summary['level'] != 'low' or config.get('macro_monitor', {}).get('alert_on_major_change', False):
        notifier.send_macro_alert(summary, config)
    
    return summary

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

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  A股风险预警系统 v2.0")
    print("="*60)
    
    # 加载配置
    try:
        config = load_config()
        print("\n[配置] 加载成功")
        
        # 检查微信通知配置
        wechat_enabled = config.get('notification', {}).get('wechat', {}).get('enabled', False)
        wechat_key = config.get('notification', {}).get('wechat', {}).get('send_key', '')
        
        if wechat_enabled and not wechat_key:
            print("[警告] 微信通知已启用但未配置SendKey")
            print("       请访问 https://sct.ftqq.com/ 获取SendKey")
            print("       然后填入 config/settings.json")
        elif wechat_enabled and wechat_key:
            print("[通知] 微信推送已启用")
        else:
            print("[通知] 仅控制台输出（未启用微信）")
            
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
    
    notifier = Notifier()
    
    # 获取监控列表
    watchlist = config.get('watchlist', [])
    
    if not watchlist:
        print("[警告] 监控列表为空，请在 config/settings.json 中添加股票")
        return
    
    print(f"[监控] 股票数量: {len(watchlist)}")
    
    # 1. 宏观经济检查
    if config.get('macro_monitor', {}).get('enabled', True):
        macro_summary = analyze_macro(fetcher, notifier, config)
    
    # 2. 个股检查
    print("\n" + "="*60)
    print("  个股风险检查")
    print("="*60)
    
    results = []
    for stock in watchlist:
        try:
            result = analyze_stock(stock, fetcher, notifier, config)
            results.append(result)
        except Exception as e:
            print(f"[错误] 分析 {stock['name']} 时出错: {e}")
    
    # 3. 汇总
    print("\n" + "="*60)
    print("  本次监控汇总")
    print("="*60)
    
    for r in results:
        emoji = {'high': '!!', 'medium': '! ', 'low': 'OK', 'safe': 'OK'}.get(r['risk_level'], '--')
        pos_info = f"[{r['position']*100:.0f}%]" if r['position'] > 0 else "[观望]"
        print(f"  [{emoji}] {r['name']} ({r['code']}) {pos_info} - {r['risk_level'].upper()}")
    
    # 持仓集中度提醒
    total_position = sum(r['position'] for r in results)
    if total_position > 0.8:
        print(f"\n  [注意] 总持仓 {total_position*100:.0f}%，集中度较高，建议适当分散")
    
    print("\n[提示] 建议每个交易日收盘后运行一次检查")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
