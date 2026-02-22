"""
A股风险预警系统 - 技术/价格风险分析
"""
import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    """技术面风险分析器"""
    
    def __init__(self, stock_config):
        self.config = stock_config
        self.risks = []
    
    def analyze(self, daily_df):
        """分析技术面风险"""
        self.risks = []
        
        if daily_df is None or daily_df.empty or len(daily_df) < 5:
            self.risks.append({
                'level': 'warning',
                'type': '数据不足',
                'desc': '行情数据不足，无法完成技术分析'
            })
            return self.risks
        
        daily_df = daily_df.sort_values('trade_date')
        latest = daily_df.iloc[-1]
        prev = daily_df.iloc[-2] if len(daily_df) > 1 else None
        
        # 1. 检查异常波动
        pct_change = float(latest['pct_chg']) if 'pct_chg' in latest else 0
        
        # 大跌预警
        threshold_drop = self.config.get('alert_threshold', {}).get('price_drop_pct', -0.08)
        if pct_change <= threshold_drop * 100:  # 转换为百分比
            self.risks.append({
                'level': 'high',
                'type': '单日大跌',
                'desc': f'当日下跌 {pct_change:.2f}%，超过 {abs(threshold_drop)*100:.0f}% 预警线',
                'value': pct_change
            })
        
        # 大涨提醒（可能考虑减仓）
        threshold_rise = self.config.get('alert_threshold', {}).get('price_rise_pct', 0.15)
        if pct_change >= threshold_rise * 100:
            self.risks.append({
                'level': 'low',
                'type': '单日大涨',
                'desc': f'当日上涨 {pct_change:.2f}%，可考虑适当减仓锁定利润',
                'value': pct_change
            })
        
        # 2. 检查连续下跌
        self._check_consecutive_decline(daily_df)
        
        # 3. 检查成交量异常
        self._check_volume_surge(daily_df)
        
        # 4. 检查均线破位
        self._check_ma_break(daily_df)
        
        # 5. 检查涨跌停
        if 'high' in latest and 'low' in latest and 'pre_close' in latest:
            pre_close = float(latest['pre_close'])
            high = float(latest['high'])
            low = float(latest['low'])
            
            # 涨停
            if high >= pre_close * 1.095:
                self.risks.append({
                    'level': 'low',
                    'type': '涨停',
                    'desc': '当日涨停，关注后续走势'
                })
            
            # 跌停
            if low <= pre_close * 0.905:
                self.risks.append({
                    'level': 'high',
                    'type': '跌停',
                    'desc': '当日跌停，需高度警惕'
                })
        
        return self.risks
    
    def _check_consecutive_decline(self, df):
        """检查连续下跌"""
        closes = df['close'].astype(float).values
        
        # 计算连续下跌天数
        consecutive_down = 0
        for i in range(len(closes)-1, 0, -1):
            if closes[i] < closes[i-1]:
                consecutive_down += 1
            else:
                break
        
        if consecutive_down >= 3:
            self.risks.append({
                'level': 'medium',
                'type': '连续下跌',
                'desc': f'连续 {consecutive_down} 个交易日下跌',
                'value': consecutive_down
            })
    
    def _check_volume_surge(self, df):
        """检查成交量异常"""
        if 'vol' not in df.columns or len(df) < 6:
            return
        
        volumes = df['vol'].astype(float).values
        latest_vol = volumes[-1]
        avg_vol_5 = np.mean(volumes[-6:-1])  # 前5日均量
        
        threshold = self.config.get('alert_threshold', {}).get('volume_surge_ratio', 2.5)
        
        if avg_vol_5 > 0 and latest_vol > avg_vol_5 * threshold:
            # 放量下跌
            pct_change = float(df.iloc[-1]['pct_chg']) if 'pct_chg' in df.iloc[-1] else 0
            if pct_change < -2:
                self.risks.append({
                    'level': 'high',
                    'type': '放量下跌',
                    'desc': f'成交量是5日均量的 {latest_vol/avg_vol_5:.1f} 倍，且股价下跌 {pct_change:.2f}%',
                    'value': latest_vol / avg_vol_5
                })
            else:
                self.risks.append({
                    'level': 'low',
                    'type': '放量上涨',
                    'desc': f'成交量是5日均量的 {latest_vol/avg_vol_5:.1f} 倍',
                    'value': latest_vol / avg_vol_5
                })
    
    def _check_ma_break(self, df):
        """检查均线破位"""
        if len(df) < 60:
            return
        
        closes = df['close'].astype(float).values
        
        # 计算均线
        ma20 = np.mean(closes[-20:])
        ma60 = np.mean(closes[-60:])
        latest_close = closes[-1]
        prev_close = closes[-2]
        
        # 跌破20日均线
        if prev_close >= ma20 and latest_close < ma20:
            self.risks.append({
                'level': 'medium',
                'type': '跌破20日均线',
                'desc': f'收盘价 {latest_close:.2f} 跌破20日均线 {ma20:.2f}',
                'value': ma20
            })
        
        # 跌破60日均线（中期趋势）
        if prev_close >= ma60 and latest_close < ma60:
            self.risks.append({
                'level': 'high',
                'type': '跌破60日均线',
                'desc': f'收盘价 {latest_close:.2f} 跌破60日均线 {ma60:.2f}，中期趋势可能转弱',
                'value': ma60
            })
    
    def get_position_advice(self, daily_df, cost_price=None):
        """基于技术面给出持仓建议"""
        if daily_df is None or daily_df.empty:
            return "数据不足，无法给出建议"
        
        latest = daily_df.iloc[-1]
        current_price = float(latest['close'])
        
        advice = []
        
        # 盈亏情况
        if cost_price:
            profit_pct = (current_price - cost_price) / cost_price * 100
            if profit_pct > 20:
                advice.append(f"当前盈利 {profit_pct:.1f}%，可考虑分批减仓锁定利润")
            elif profit_pct < -15:
                advice.append(f"当前亏损 {abs(profit_pct):.1f}%，需评估是否止损")
        
        return "；".join(advice) if advice else "技术面暂无明确操作建议"
