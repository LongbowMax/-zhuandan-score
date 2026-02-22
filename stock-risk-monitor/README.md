# A股风险预警系统 V2.0

**专为稳健型投资者设计的中长期持仓风险监控工具**

---

## 功能特性

- **多股票监控** — 支持同时监控多只股票
- **基本面分析** — 营收、利润、ROE、负债、现金流
- **技术面分析** — 价格异动、均线破位、成交量异常
- **宏观经济监控** — Shibor、CPI、PMI、汇率
- **微信通知** — 通过Server酱推送到微信
- **定时任务** — 可设置自动运行

---

## 快速开始

### 1. 运行监控

```bash
cd stock-risk-monitor
python main.py
```

或双击 `run.bat`

### 2. 配置微信通知

1. 访问 https://sct.ftqq.com/ 用GitHub登录
2. 获取 **SendKey**
3. 编辑 `config/settings.json`，填入SendKey：

```json
{
  "notification": {
    "wechat": {
      "enabled": true,
      "send_key": "SCT你的SendKey"
    }
  }
}
```

### 3. 添加股票

编辑 `config/settings.json` 中的 `watchlist`：

```json
"watchlist": [
  {
    "code": "600995",
    "name": "南网储能",
    "position_ratio": 0.70,
    "cost_price": 12.50
  },
  {
    "code": "000001", 
    "name": "平安银行",
    "position_ratio": 0.20,
    "cost_price": 10.00
  }
]
```

---

## 查看详细指南

[GUIDE.md](GUIDE.md) — 包含完整配置说明、定时任务设置、FAQ

---

## 项目结构

```
stock-risk-monitor/
├── main.py                 # 主程序
├── run.bat                 # Windows启动脚本
├── config/
│   └── settings.json       # 配置文件
├── modules/
│   ├── data_fetcher.py     # 数据获取
│   ├── fundamental_check.py # 基本面分析
│   ├── technical_analyzer.py # 技术面分析
│   ├── macro_monitor.py    # 宏观经济监控
│   └── notifier.py         # 通知模块
├── reports/                # 分析报告
└── README.md               # 本文件
```

---

## 风险等级说明

| 等级 | 图标 | 含义 | 建议 |
|------|------|------|------|
| HIGH | !! | 高风险 | 建议立即评估持仓 |
| MEDIUM | ! | 中等风险 | 需要关注 |
| LOW | OK | 低风险 | 正常监控 |
| SAFE | OK | 安全 | 无异常 |

---

## 免责声明

本系统仅供学习研究使用，不构成任何投资建议。股市有风险，投资需谨慎。

---

⚒️🏔️ 山鬼之锤
