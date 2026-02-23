"""
A股风险预警系统 - 数据获取模块
使用Tushare获取股票数据
"""
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class DataFetcher:
    def __init__(self, config_path='config/settings.json'):
        """初始化Tushare连接"""
        # 获取模块所在目录，构建正确路径
        module_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(module_dir)
        full_config_path = os.path.join(project_dir, config_path)
        
        with open(full_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.token = config.get('tushare', {}).get('token', '')
        if not self.token:
            raise ValueError("Tushare Token 未配置，请在 config/settings.json 中设置 tushare.token")
        
        ts.set_token(self.token)
        self.pro = ts.pro_api()
        self.config = config
    
    def get_stock_basic(self, ts_code):
        """获取股票基本信息"""
        try:
            df = self.pro.stock_basic(ts_code=ts_code)
            return df.to_dict('records')[0] if not df.empty else None
        except Exception as e:
            print(f"获取股票基本信息失败: {e}")
            return None
    
    def get_daily_data(self, ts_code, days=30):
        """获取日线数据"""
        try:
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            if df is not None and not df.empty:
                df = df.sort_values('trade_date')
            return df
        except Exception as e:
            print(f"获取日线数据失败: {e}")
            return None
    
    def get_financial_data(self, ts_code):
        """获取最新财务数据"""
        try:
            # 最新一期财务指标
            df = self.pro.fina_indicator(ts_code=ts_code, limit=4)
            return df if df is not None and not df.empty else None
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return None
    
    def get_express_data(self, ts_code):
        """获取业绩快报"""
        try:
            df = self.pro.express(ts_code=ts_code, limit=2)
            return df if df is not None and not df.empty else None
        except Exception as e:
            print(f"获取业绩快报失败: {e}")
            return None
    
    def get_forecast_data(self, ts_code):
        """获取业绩预告"""
        try:
            df = self.pro.forecast(ts_code=ts_code, limit=2)
            return df if df is not None and not df.empty else None
        except Exception as e:
            print(f"获取业绩预告失败: {e}")
            return None
    
    def get_major_news(self, ts_code, start_date=None, end_date=None):
        """获取公司重大公告"""
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            df = self.pro.major_news(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df if df is not None and not df.empty else None
        except Exception as e:
            print(f"获取公告失败: {e}")
            return None
    
    def get_industry_info(self, ts_code):
        """获取所属行业信息"""
        try:
            df = self.pro.stock_company(ts_code=ts_code)
            return df.to_dict('records')[0] if df is not None and not df.empty else None
        except Exception as e:
            print(f"获取行业信息失败: {e}")
            return None

if __name__ == '__main__':
    # 测试
    fetcher = DataFetcher()
    # 南网储能：600995.SH
    print("测试获取日线数据...")
    data = fetcher.get_daily_data('600995.SH', days=10)
    print(data.head() if data is not None else "无数据")
