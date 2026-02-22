"""
A股风险预警系统 - 宏观经济监控模块
监控：Shibor、CPI、PMI、汇率等宏观指标
"""
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

class MacroMonitor:
    """宏观经济监控器"""
    
    # 风险阈值
    THRESHOLDS = {
        'shibor_spike': 0.5,        # Shibor单日上升50bp预警
        'cpi_high': 3.0,             # CPI超过3%预警
        'pmi_contraction': 50.0,     # PMI低于50预警
        'usdcny_volatility': 0.02,   # 人民币汇率波动2%预警
    }
    
    def __init__(self, pro_api):
        self.pro = pro_api
        self.alerts = []
    
    def check_all(self):
        """检查所有宏观指标"""
        self.alerts = []
        
        print("\n[宏观经济监控]")
        
        # 1. 检查Shibor（银行间利率，反映流动性）
        self._check_shibor()
        
        # 2. 检查CPI（通胀水平）
        self._check_cpi()
        
        # 3. 检查PMI（经济景气度）
        self._check_pmi()
        
        # 4. 检查汇率（人民币汇率波动）
        self._check_exchange_rate()
        
        return self.alerts
    
    def _check_shibor(self):
        """检查Shibor利率变化"""
        try:
            # 获取最近10天的Shibor隔夜利率
            df = self.pro.shibor(start_date=(datetime.now()-timedelta(days=30)).strftime('%Y%m%d'),
                                 end_date=datetime.now().strftime('%Y%m%d'))
            
            if df is not None and len(df) >= 2:
                df = df.sort_values('date')
                latest = float(df.iloc[-1]['on'])  # 隔夜利率
                prev = float(df.iloc[-2]['on'])
                change = latest - prev
                
                print(f"  Shibor隔夜: {latest:.3f}% (较昨日{change:+.3f}%)")
                
                if change >= self.THRESHOLDS['shibor_spike']:
                    self.alerts.append({
                        'level': 'high',
                        'type': '流动性收紧',
                        'indicator': 'Shibor',
                        'desc': f'隔夜Shibor单日跳升 {change:.3f}%，市场流动性可能收紧',
                        'value': latest,
                        'change': change
                    })
                elif latest > 2.5:  # 利率处于高位
                    self.alerts.append({
                        'level': 'medium',
                        'type': '利率偏高',
                        'indicator': 'Shibor',
                        'desc': f'隔夜Shibor处于 {latest:.3f}% 的相对高位',
                        'value': latest
                    })
        except Exception as e:
            print(f"  Shibor数据获取失败: {e}")
    
    def _check_cpi(self):
        """检查CPI数据"""
        try:
            # 使用宏观数据接口
            df = self.pro.cn_cpi(start_m='202401', end_m=datetime.now().strftime('%Y%m'))
            
            if df is not None and not df.empty:
                df = df.sort_values('month', ascending=False)
                latest = df.iloc[0]
                cpi_yoy = float(latest['cpi_yoy']) if 'cpi_yoy' in latest else None
                month = latest['month']
                
                if cpi_yoy:
                    print(f"  CPI {month}: 同比 {cpi_yoy:.1f}%")
                    
                    if cpi_yoy >= self.THRESHOLDS['cpi_high']:
                        self.alerts.append({
                            'level': 'medium',
                            'type': '通胀压力',
                            'indicator': 'CPI',
                            'desc': f'CPI同比 {cpi_yoy:.1f}%，通胀水平较高，可能引发货币政策收紧',
                            'value': cpi_yoy
                        })
        except Exception as e:
            print(f"  CPI数据获取失败: {e}")
    
    def _check_pmi(self):
        """检查PMI数据"""
        try:
            # 获取制造业PMI
            df = self.pro.cn_pmi(start_date=(datetime.now()-timedelta(days=60)).strftime('%Y%m'),
                                end_date=datetime.now().strftime('%Y%m'))
            
            if df is not None and not df.empty:
                df = df.sort_values('month', ascending=False)
                latest = df.iloc[0]
                pmi = float(latest['pmi']) if 'pmi' in latest else None
                month = latest['month']
                
                if pmi:
                    status = "扩张" if pmi >= 50 else "收缩"
                    print(f"  制造业PMI {month}: {pmi:.1f} ({status})")
                    
                    if pmi < self.THRESHOLDS['pmi_contraction']:
                        self.alerts.append({
                            'level': 'high',
                            'type': '经济收缩',
                            'indicator': 'PMI',
                            'desc': f'制造业PMI {pmi:.1f} 低于荣枯线，经济处于收缩区间',
                            'value': pmi
                        })
        except Exception as e:
            print(f"  PMI数据获取失败: {e}")
    
    def _check_exchange_rate(self):
        """检查人民币汇率"""
        try:
            # 获取美元兑人民币汇率
            df = self.pro.fx_daily(ts_code='USDCNH.FXCM', 
                                  start_date=(datetime.now()-timedelta(days=10)).strftime('%Y%m%d'),
                                  end_date=datetime.now().strftime('%Y%m%d'))
            
            if df is not None and len(df) >= 2:
                df = df.sort_values('trade_date')
                latest = float(df.iloc[-1]['close'])
                prev_week = float(df.iloc[0]['close'])
                change_pct = (latest - prev_week) / prev_week
                
                print(f"  人民币汇率: {latest:.4f} (周波动 {change_pct*100:+.2f}%)")
                
                if abs(change_pct) >= self.THRESHOLDS['usdcny_volatility']:
                    direction = "贬值" if change_pct > 0 else "升值"
                    self.alerts.append({
                        'level': 'medium',
                        'type': f'汇率{direction}',
                        'indicator': 'USDCNY',
                        'desc': f'人民币对美元一周{direction} {abs(change_pct)*100:.2f}%，汇率波动加大',
                        'value': latest,
                        'change': change_pct
                    })
        except Exception as e:
            print(f"  汇率数据获取失败: {e}")
    
    def get_summary(self):
        """获取宏观监控摘要"""
        if not self.alerts:
            return {
                'status': 'safe',
                'level': 'low',
                'message': '宏观环境稳定，暂无系统性风险',
                'count': 0,
                'alerts': []
            }
        
        high_risks = [a for a in self.alerts if a['level'] == 'high']
        medium_risks = [a for a in self.alerts if a['level'] == 'medium']
        
        if high_risks:
            return {
                'status': 'danger',
                'level': 'high',
                'message': f'发现 {len(high_risks)} 项宏观高风险信号',
                'count': len(self.alerts),
                'alerts': self.alerts
            }
        elif medium_risks:
            return {
                'status': 'warning',
                'level': 'medium',
                'message': f'发现 {len(medium_risks)} 项宏观风险需关注',
                'count': len(self.alerts),
                'alerts': self.alerts
            }
        else:
            return {
                'status': 'caution',
                'level': 'low',
                'message': f'发现 {len(self.alerts)} 项轻微宏观变化',
                'count': len(self.alerts),
                'alerts': self.alerts
            }

if __name__ == '__main__':
    import json
    
    with open('../config/settings.json', 'r') as f:
        config = json.load(f)
    
    ts.set_token(config['tushare_token'])
    pro = ts.pro_api()
    
    monitor = MacroMonitor(pro)
    alerts = monitor.check_all()
    summary = monitor.get_summary()
    
    print(f"\n汇总: {summary['message']}")
