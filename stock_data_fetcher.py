import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import ta
from tqdm import tqdm


def calculate_technical_indicators(df):
    """计算技术指标"""
    df["RSI"] = ta.momentum.RSIIndicator(close=df["close"], window=14).rsi()
    macd = ta.trend.MACD(close=df["close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_hist"] = macd.macd_diff()
    df["MA20"] = ta.trend.SMAIndicator(close=df["close"], window=20).sma_indicator()
    df["MA50"] = ta.trend.SMAIndicator(close=df["close"], window=50).sma_indicator()
    bollinger = ta.volatility.BollingerBands(close=df["close"])
    df["BB_upper"] = bollinger.bollinger_hband()
    df["BB_lower"] = bollinger.bollinger_lband()
    df["BB_middle"] = bollinger.bollinger_mavg()
    return df


def get_stock_data(stock_code, start_date, end_date, listing_date=None):
    """获取单只股票的历史数据"""
    max_retries = 3
    retry_delay = 1  # 初始延迟1秒
    for attempt in range(max_retries):
        try:
            # 不添加市场前缀，直接使用原始股票代码
            symbol = stock_code

            # 如果有上市日期，确保开始日期不早于上市日期
            if listing_date:
                listing_date = pd.to_datetime(listing_date).strftime("%Y%m%d")
                if start_date < listing_date:
                    start_date = listing_date

            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq",
            )
            if df.empty:
                raise ValueError("返回的数据为空")

            df = df.rename(
                columns={
                    "日期": "date",
                    "股票代码": "code",
                    "成交额": "amount",
                    "振幅": "amplitude",
                    "涨跌幅": "pct_change",
                    "涨跌额": "price_change",
                    "换手率": "turnover_rate",
                    "开盘": "open",
                    "最高": "high",
                    "最低": "low",
                    "收盘": "close",
                    "成交量": "volume",
                }
            )
            df["date"] = pd.to_datetime(df["date"])
            df = calculate_technical_indicators(df)
            return df
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"获取{stock_code} 数据时出错（第{attempt+1}次重试）: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                with open("./data/error_log.txt", "a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {stock_code} | {str(e)}\n")
                print(f"\n{stock_code} 数据获取失败，已记录到error_log.txt")
                return None


def get_stock_news(stock_code):
    """获取个股新闻数据"""
    max_retries = 3
    retry_delay = 1  # 初始延迟1秒
    for attempt in range(max_retries):
        try:
            df = ak.stock_news_em(symbol=stock_code)
            if not df.empty:
                return df
            return None
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"获取{stock_code}新闻数据时出错（第{attempt+1}次重试）: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                with open("./data/error_log.txt", "a") as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {stock_code} 新闻 | {str(e)}\n")
                print(f"\n{stock_code}新闻数据获取失败，已记录到error_log.txt")
                return None


def main():
    end_date = datetime.now().strftime("%Y%m%d")
    default_start_date = (datetime.now() - timedelta(days=365 * 10)).strftime("%Y%m%d")

    # 获取中证500成分股列表
    stock_list = ak.index_stock_cons(symbol="000905")

    os.makedirs("./data", exist_ok=True)

    failed_stocks = []

    pbar = tqdm(stock_list.iterrows(), total=len(stock_list))
    for index, row in pbar:
        stock_code = row["品种代码"]
        stock_name = row["品种名称"]
        listing_date = row["纳入日期"]

        pbar.set_description(f"Processing {stock_code} - {stock_name}")

        df = get_stock_data(stock_code, default_start_date, end_date, listing_date)

        if df is not None:
            filename = f"./data/stock_data_{stock_code}.csv"
            df.to_csv(filename, index=False)
            pbar.write(f"已实时保存 {stock_code} 数据到 {filename}")
        else:
            failed_stocks.append(stock_code)

        # time.sleep(1)

    # 生成失败股票报告
    if failed_stocks:
        report_filename = "./data/failed_stocks_report.txt"
        with open(report_filename, "w") as report_file:
            report_file.write("Failed stock codes:\n")
            for code in failed_stocks:
                report_file.write(f"{code}\n")
        print(f"\n生成失败股票报告，共{len(failed_stocks)}只股票失败，已保存至 {report_filename}")

    # 创建新闻数据目录
    os.makedirs("./data/news", exist_ok=True)
    
    # 为每支股票获取新闻数据
    print("\n开始获取个股新闻数据...")
    news_pbar = tqdm(stock_list.iterrows(), total=len(stock_list), desc="Processing Stock News")
    for index, row in news_pbar:
        stock_code = row["品种代码"]
        stock_name = row["品种名称"]
        
        news_pbar.set_description(f"Processing News for {stock_code} - {stock_name}")
        
        # 创建每支股票的新闻目录
        stock_news_dir = f"./data/news"
        os.makedirs(stock_news_dir, exist_ok=True)
        
        # 获取个股新闻
        news_df = get_stock_news(stock_code)
        
        if news_df is not None and not news_df.empty:
            news_filename = f"{stock_news_dir}/news_{stock_code}.csv"
            news_df.to_csv(news_filename, index=False)
            news_pbar.write(f"已实时保存 {stock_code} 新闻数据到 {news_filename}")
        else:
            news_pbar.write(f"未获取到 {stock_code} 的新闻数据")
            
        # 避免请求过于频繁
        time.sleep(0.5)

    return None


if __name__ == "__main__":
    # 测试 AKShare 功能
    print("测试 AKShare 功能...")
    try:
        test_df = ak.stock_zh_a_hist(
            symbol="600519",
            period="daily",
            start_date="20200101",
            end_date="20250331",
            adjust="qfq",
        )
        print("测试成功，获取到茅台数据：")
        print(test_df.head())
    except Exception as e:
        print(f"测试失败，AKShare 可能有问题: {str(e)}")

    # 运行主程序
    main()
    print("\n数据采集完成，所有CSV文件已保存至data目录")
