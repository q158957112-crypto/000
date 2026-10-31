import os
import requests

# 1. 填入你目前的持有股數與短債買入張數
# 00631L: 44,150 股, 00685L: 視截圖約 5,800 股 (請依實際調整)
HOLDINGS = {
    "00631L.TW": 44150,
    "00685L.TW": 5800,
    "00865B.TW": 12000,  # 預計買入 12 張 (12,000 股)
}

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def get_stock_price(ticker):
    """取得股票/ETF 最新價格"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
        return price
    except Exception as e:
        print(f"抓取 {ticker} 價格失敗: {e}")
        return None

def main():
    p_631 = get_stock_price("00631L.TW")
    p_685 = get_stock_price("00685L.TW")
    p_865 = get_stock_price("00865B.TW")
    
    if not (p_631 and p_685 and p_865):
        print("無法取得部分資產價格，跳過今日檢查")
        return

    # 計算各項資產總市值
    val_leveraged = (HOLDINGS["00631L.TW"] * p_631) + (HOLDINGS["00685L.TW"] * p_685)
    val_bond = HOLDINGS["00865B.TW"] * p_865
    total_val = val_leveraged + val_bond

    # 計算實際比例
    ratio_leveraged = (val_leveraged / total_val) * 100
    ratio_bond = (val_bond / total_val) * 100

    # 檢測是否有顯著偏離（目標 80% 正二 / 20% 短債，觸發門檻：偏離超過 ±5%）
    is_overloaded = ratio_leveraged > 85.0  # 股市大漲，正二佔比 > 85%
    is_underloaded = ratio_leveraged < 75.0 # 股市大跌，正二佔比 < 75%

    if is_overloaded or is_underloaded:
        status_title = "🚨 【再平衡提醒】資產比例已偏離預定目標！"
        if is_overloaded:
            suggestion = f"📈 **正二比重過高 ({ratio_leveraged:.1f}%)**：建議賣出部分正二，轉入 00865B 鎖定獲利。"
        else:
            suggestion = f"📉 **正二比重過低 ({ratio_leveraged:.1f}%)**：建議賣出部分 00865B，加碼低點正二抄底！"
        
        message = (
            f"### {status_title}\n"
            f"- **總資產估值**：${total_val:,.0f} TWD\n"
            f"- **正二總市值**：${val_leveraged:,.0f} ({ratio_leveraged:.1f}%)\n"
            f"- **00865B 市值**：${val_bond:,.0f} ({ratio_bond:.1f}%)\n\n"
            f"{suggestion}"
        )
        
        # 推播至 Discord
        if DISCORD_WEBHOOK_URL:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": message})
            print("通知已發送至 Discord")
        else:
            print("未設定 Webhook，訊息內容如下：")
            print(message)
    else:
        print(f"目前資產比例正常（正二: {ratio_leveraged:.1f}% / 短債: {ratio_bond:.1f}%），無需再平衡。")

if __name__ == "__main__":
    main()
