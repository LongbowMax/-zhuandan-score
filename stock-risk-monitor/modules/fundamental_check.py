"""
A股风险预警系统 - 基本面风险分析
针对南网储能的检查项
"""
import pandas as pd
from datetime import datetime

class FundamentalAnalyzer:
    """基本面风险分析器"""
    
    # 风险阈值配置
    RISK_THRESHOLDS = {
        'revenue_decline': -0.10,      # 营收下滑超过10%预警
        'profit_decline': -0.20,       # 净利润下滑超过20%预警
        'roe_decline': -0.15,          # ROE下滑超过15%预警
        'debt_ratio_high': 0.70,       # 资产负债率超过70%预警
        'cashflow_negative': 0,        # 经营现金流为负预警
    }
    
    def __init__(self):
        self.risks = []
    
    def analyze_financial_data(self, fin_df):
        """分析财务数据"""
        self.risks = []
        
        if fin_df is None or fin_df.empty:
            self.risks.append({
                'level': 'warning',
                'type': '数据缺失',
                'desc': '无法获取财务数据，请检查数据源权限'
            })
            return self.risks
        
        fin_df = fin_df.sort_values('end_date', ascending=False)
        latest = fin_df.iloc[0]
        
        # 检查营收同比
        if 'or_yoy' in latest:
            revenue_yoy = float(latest['or_yoy']) if pd.notna(latest['or_yoy']) else 0
            if revenue_yoy < self.RISK_THRESHOLDS['revenue_decline'] * 100:
                self.risks.append({
                    'level': 'high',
                    'type': '营收下滑',
                    'desc': f'营业收入同比下降 {revenue_yoy:.2f}%，需关注业务增长情况',
                    'value': revenue_yoy
                })
        
        # 检查净利润同比
        if 'netprofit_yoy' in latest:
            profit_yoy = float(latest['netprofit_yoy']) if pd.notna(latest['netprofit_yoy']) else 0
            if profit_yoy < self.RISK_THRESHOLDS['profit_decline'] * 100:
                self.risks.append({
                    'level': 'high',
                    'type': '净利润大幅下滑',
                    'desc': f'净利润同比下降 {profit_yoy:.2f}%，基本面可能恶化',
                    'value': profit_yoy
                })
            elif profit_yoy < 0:
                self.risks.append({
                    'level': 'medium',
                    'type': '净利润下滑',
                    'desc': f'净利润同比下降 {profit_yoy:.2f}%',
                    'value': profit_yoy
                })
        
        # 检查ROE
        if 'roe' in latest:
            roe = float(latest['roe']) if pd.notna(latest['roe']) else 0
            if len(fin_df) > 1:
                prev_roe = float(fin_df.iloc[1]['roe']) if pd.notna(fin_df.iloc[1]['roe']) else roe
                roe_change = (roe - prev_roe) / prev_roe if prev_roe != 0 else 0
                if roe_change < self.RISK_THRESHOLDS['roe_decline']:
                    self.risks.append({
                        'level': 'medium',
                        'type': 'ROE下降',
                        'desc': f'ROE从 {prev_roe:.2f}% 降至 {roe:.2f}%，盈利能力减弱',
                        'value': roe
                    })
        
        # 检查资产负债率
        if 'debt_to_assets' in latest:
            debt_ratio = float(latest['debt_to_assets']) if pd.notna(latest['debt_to_assets']) else 0
            if debt_ratio > self.RISK_THRESHOLDS['debt_ratio_high'] * 100:
                self.risks.append({
                    'level': 'medium',
                    'type': '高负债率',
                    'desc': f'资产负债率 {debt_ratio:.2f}%，财务杠杆较高',
                    'value': debt_ratio
                })
        
        # 检查经营现金流
        if 'ocfps' in latest:
            ocfps = float(latest['ocfps']) if pd.notna(latest['ocfps']) else 0
            if ocfps < 0:
                self.risks.append({
                    'level': 'medium',
                    'type': '经营现金流为负',
                    'desc': f'每股经营现金流 {ocfps:.2f} 元，主营业务回款能力下降',
                    'value': ocfps
                })
        
        # 检查毛利率
        if 'grossprofit_margin' in latest:
            gpm = float(latest['grossprofit_margin']) if pd.notna(latest['grossprofit_margin']) else 0
            if len(fin_df) > 1:
                prev_gpm = float(fin_df.iloc[1]['grossprofit_margin']) if pd.notna(fin_df.iloc[1]['grossprofit_margin']) else gpm
                if gpm < prev_gpm * 0.9:  # 毛利率下降超过10%
                    self.risks.append({
                        'level': 'low',
                        'type': '毛利率下降',
                        'desc': f'毛利率从 {prev_gpm:.2f}% 降至 {gpm:.2f}%',
                        'value': gpm
                    })
        
        return self.risks
    
    def analyze_express_report(self, express_df):
        """分析业绩快报"""
        if express_df is None or express_df.empty:
            return []
        
        express_risks = []
        latest = express_df.iloc[0]
        
        # 业绩快报中的利润变化
        if 'profit_yoy' in latest:
            profit_yoy = float(latest['profit_yoy']) if pd.notna(latest['profit_yoy']) else 0
            if profit_yoy < -20:
                express_risks.append({
                    'level': 'high',
                    'type': '业绩快报：利润大幅下滑',
                    'desc': f'业绩快报显示净利润同比下降 {profit_yoy:.2f}%',
                    'value': profit_yoy
                })
        
        return express_risks
    
    def analyze_forecast(self, forecast_df):
        """分析业绩预告"""
        if forecast_df is None or forecast_df.empty:
            return []
        
        forecast_risks = []
        latest = forecast_df.iloc[0]
        
        # 预告类型
        if 'type' in latest:
            forecast_type = latest['type']
            if '预减' in forecast_type or '预亏' in forecast_type:
                forecast_risks.append({
                    'level': 'high',
                    'type': f'业绩预告：{forecast_type}',
                    'desc': f'公司发布{forecast_type}预告，需高度警惕',
                    'value': forecast_type
                })
            elif '略减' in forecast_type:
                forecast_risks.append({
                    'level': 'medium',
                    'type': f'业绩预告：{forecast_type}',
                    'desc': f'公司发布{forecast_type}预告',
                    'value': forecast_type
                })
        
        return forecast_risks
    
    def get_summary(self):
        """获取风险汇总"""
        if not self.risks:
            return {
                'status': 'safe',
                'level': 'low',
                'message': '未发现明显基本面风险',
                'count': 0,
                'risks': []
            }
        
        high_risks = [r for r in self.risks if r['level'] == 'high']
        medium_risks = [r for r in self.risks if r['level'] == 'medium']
        low_risks = [r for r in self.risks if r['level'] == 'low']
        
        if high_risks:
            return {
                'status': 'danger',
                'level': 'high',
                'message': f'发现 {len(high_risks)} 项高风险，建议立即评估持仓',
                'count': len(self.risks),
                'high_count': len(high_risks),
                'risks': self.risks
            }
        elif medium_risks:
            return {
                'status': 'warning',
                'level': 'medium',
                'message': f'发现 {len(medium_risks)} 项中等风险，建议关注',
                'count': len(self.risks),
                'risks': self.risks
            }
        else:
            return {
                'status': 'caution',
                'level': 'low',
                'message': f'发现 {len(low_risks)} 项轻微风险',
                'count': len(self.risks),
                'risks': self.risks
            }
