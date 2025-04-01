<!--
 * @Author: fx-k admin@fxit.top
 * @Date: 2025-04-01 17:09:10
 * @LastEditors: fx-k admin@fxit.top
 * @LastEditTime: 2025-04-01 17:50:50
 * @FilePath: /csi500-stock-analysis/README.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
# CSI500 Stock Analysis

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

专业的中证500成分股历史数据分析工具，集成新闻联播文本分析功能。

## 项目概述
本工具自动化采集沪深交易所中证500指数成分股的完整历史交易数据（2014-2024），同步抓取对应时期的央视新闻联播文本数据。提供30+技术指标计算、数据持久化存储及错误追踪功能。

## 功能特性
- **自动化数据采集**：全自动爬取股票代码/名称/上市日期
- **多维数据抓取**：包含开盘价、收盘价、成交量等15+交易维度
- **智能技术指标**：实时计算RSI、MACD、布林带等30+技术指标
- **新闻舆情分析**：同步获取新闻联播文本数据（标题+正文）
- **持久化存储**：自动生成CSV文件并按日期分类存储
- **错误追踪系统**：自动记录失败股票代码及错误日志

## 目录结构
```
.
├── data/                           # 数据存储目录
│   ├── stock_data_*.csv           # 个股历史数据文件
│   ├── news/                      # 新闻数据目录
│   │   └── news_YYYYMMDD.csv      # 每日新闻文件
│   ├── error_log.txt              # 错误日志
│   └── failed_stocks_report.txt   # 失败股票记录
├── requirements.txt               # 依赖库列表
└── stock_data_fetcher.py          # 主程序
```

## 安装指引
```bash
# 克隆仓库
git clone https://github.com/fx-k/csi500-stock-analysis.git

# 安装依赖
pip install -r requirements.txt

# 推荐使用Python 3.8+环境
```

## 使用说明
```python
# 运行主程序（自动下载全部数据）
python stock_data_fetcher.py

```

## 技术指标计算
| 指标类型       | 包含指标                              | 计算周期 |
|----------------|-------------------------------------|----------|
| 动量指标       | RSI, MACD, Stochastic Oscillator    | 14天     |
| 趋势指标       | MA(20/50), Parabolic SAR, ADX      | 20/50天 |
| 波动率指标     | Bollinger Bands, ATR                | 20天     |
| 成交量指标     | OBV, Chaikin Money Flow             | N/A      |

## 数据采集范围
- **股票数据**：2014年1月1日 - 当日数据
- **新闻数据**：每个交易日对应日期的新闻联播全文
- **更新频率**：每日自动增量更新

## 许可协议
本项目采用 [MIT License](LICENSE)