# A股风险预警系统 - 使用指南

## 快速开始

### 1. 运行监控

双击 `run.bat` 或在命令行运行：
```bash
cd stock-risk-monitor
python main.py
```

### 2. 配置微信通知

#### 步骤1：注册 Server酱
1. 访问 https://sct.ftqq.com/
2. 点击右上角「GitHub登录」，用你的GitHub账号授权
3. 登录后会看到 **SendKey**，类似这样：
   ```
   SCT1234567890abcdefghijklmnopqrstuv
   ```

#### 步骤2：配置到系统
编辑 `config/settings.json`：
```json
{
  "notification": {
    "channels": ["console", "wechat"],
    "wechat": {
      "enabled": true,
      "send_key": "SCT你的SendKey",
      "type": "serverchan"
    }
  }
}
```

#### 步骤3：测试
运行程序，检查微信是否收到通知。

---

## 添加/删除股票

编辑 `config/settings.json` 中的 `watchlist`：

```json
"watchlist": [
  {
    "code": "600995",
    "name": "南网储能",
    "position_ratio": 0.70,
    "cost_price": 12.50,
    "sector": "电力",
    "alert_threshold": {
      "price_drop_pct": -0.08,
      "price_rise_pct": 0.15,
      "volume_surge_ratio": 2.5
    }
  },
  {
    "code": "000001",
    "name": "平安银行",
    "position_ratio": 0.20,
    "cost_price": 10.00,
    "sector": "银行",
    "alert_threshold": {
      "price_drop_pct": -0.05,
      "price_rise_pct": 0.10,
      "volume_surge_ratio": 3.0
    }
  }
]
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `code` | 股票代码 | "600995" |
| `name` | 股票名称 | "南网储能" |
| `position_ratio` | 持仓比例（0-1）| 0.70 = 70% |
| `cost_price` | 持仓成本价 | 12.50 |
| `sector` | 所属行业 | "电力" |
| `price_drop_pct` | 下跌预警阈值 | -0.08 = -8% |
| `price_rise_pct` | 上涨提醒阈值 | 0.15 = +15% |

---

## 宏观经济监控

系统默认监控以下宏观指标：

| 指标 | 说明 | 预警条件 |
|------|------|----------|
| **Shibor** | 银行间利率 | 单日跳升50bp |
| **CPI** | 通胀水平 | 超过3% |
| **PMI** | 经济景气度 | 低于50（收缩） |
| **USDCNY** | 人民币汇率 | 周波动超2% |

配置在 `settings.json`：
```json
"macro_monitor": {
  "enabled": true,
  "indicators": ["shibor", "cpi", "pmi", "usdcny"],
  "alert_on_major_change": true
}
```

---

## 政策监控

监控电力、储能、新能源相关政策：

```json
"policy_monitor": {
  "enabled": true,
  "sectors": ["电力", "储能", "新能源"],
  "keywords": ["电价", "储能", "新能源", "电力改革"]
}
```

---

## 设置定时任务

### Windows 任务计划程序

1. 按 `Win+R`，输入 `taskschd.msc` 回车
2. 右侧点击「创建基本任务」
3. 名称：`A股风险检查`
4. 触发器：每天 15:30（收盘后）
5. 操作：启动程序
6. 程序：`C:\Users\hp\.openclaw\workspace\stock-risk-monitor\run.bat`

### 多个时间点

建议设置两个任务：
- **午间检查**：12:00（早盘结束后）
- **收盘检查**：15:30（全天结束后）

---

## 通知规则

| 场景 | 通知方式 |
|------|----------|
| 持仓股票出现中高风险 | 微信 + 控制台 |
| 持仓股票正常 | 仅控制台（节省微信次数） |
| 宏观指标异常 | 微信 + 控制台 |
| 非持仓股票仅高风险 | 微信 + 控制台 |

---

## 常见问题

### Q: 微信收不到通知？
A: 检查以下几点：
1. SendKey 是否正确复制（不要有多余空格）
2. `enabled` 是否设置为 `true`
3. `channels` 是否包含 `"wechat"`
4. Server酱免费版每天限20条推送

### Q: 如何修改预警阈值？
A: 在 `watchlist` 中每只股票下修改 `alert_threshold`。

### Q: 支持港股/美股吗？
A: 当前版本仅支持A股。如需港股美股，可使用Tushare Pro的港股/美股接口，但需要修改代码。

### Q: 数据更新频率？
- 日线数据：每日收盘后更新
- 财务数据：季报期更新
- 宏观数据：月度更新

---

## 风险提示

1. **本系统仅供参考，不构成投资建议**
2. 股市有风险，投资需谨慎
3. 建议结合自身判断和多种信息源做决策

---

_最后更新: 2026-02-20_
