import os
import requests

# 1. 填入你目前的持有股數 (未來買賣時請更新這裡的數字)
HOLDINGS = {
    "00631L.TW": 44150,  # 元大台灣50正2
    "00685L.TW": 5800,   # 富邦台灣加權正2
    "00865B.TW": 12000,  # 國泰 US 短期公債 (12張)
}

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_message(msg):
    """發送訊息至 Discord Webhook"""
    if DISCORD_WEBHOOK_URL:
        try:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": msg}, timeout=10)
        except Exception as e:
            print(f"發送 Discord 訊息失敗: {e}")
    else:
        print("未設定 Webhook，訊息內容如下：\n" + msg)

def get_stock_data(ticker):
    """取得股票/ETF 最新價格與前一交易日收盤價"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        meta = data["chart"]["result"][0]["meta"]
        
        current_price = meta.get("regularMarketPrice")
        previous_close = meta.get("chartPreviousClose") or meta.get("previousClose")
        
        return current_price, previous_close
    except Exception as e:
        print(f"抓取 {ticker} 資料失敗: {e}")
        return None, None

def main():
    # 抓取三支標的的即時與昨收價格
    p_631, prev_631 = get_stock_data("00631L.TW")
    p_685, prev_685 = get_stock_data("00685L.TW")
    p_865, prev_865 = get_stock_data("00865B.TW")
    
    # API 抓取失敗警報
    if not (p_631 and p_685 and p_865 and prev_631 and prev_685 and prev_865):
        error_msg = "⚠️ **【系統警告】無法成功取得最新股價數據！**\n請檢查 Yahoo Finance API 或連線狀態。"
        print(error_msg)
        send_discord_message(error_msg)
        return

    # 計算今日總市值與昨日總市值
    val_631 = HOLDINGS["00631L.TW"] * p_631
    val_685 = HOLDINGS["00685L.TW"] * p_685
    val_865 = HOLDINGS["00865B.TW"] * p_865

    prev_val_631 = HOLDINGS["00631L.TW"] * prev_631
    prev_val_685 = HOLDINGS["00685L.TW"] * prev_685
    prev_val_865 = HOLDINGS["00865B.TW"] * prev_865

    val_leveraged = val_631 + val_685
    val_bond = val_865
    total_val = val_leveraged + val_bond
    prev_total_val = prev_val_631 + prev_val_685 + prev_val_865

    # 計算今日損益金額與百分比 (Daily P&L)
    daily_change = total_val - prev_total_val
    daily_change_pct = (daily_change / prev_total_val) * 100
    
    sign = "+" if daily_change >= 0 else ""
    pnl_str = f"{sign}${daily_change:,.0f} TWD ({sign}{daily_change_pct:.2f}%)"

    # 計算實際資產比例
    ratio_leveraged = (val_leveraged / total_val) * 100
    ratio_bond = (val_bond / total_val) * 100

    # 判定是否觸發比例偏移 (目標 80% 正二，門檻 ±5%)
    is_overloaded = ratio_leveraged > 85.0
    is_underloaded = ratio_leveraged < 75.0

    # 組合狀態標題與建議
    if is_overloaded or is_underloaded:
        title = "🚨 **【再平衡提醒】資產比例已顯著偏離！**"
        if is_overloaded:
            suggestion = f"📈 **正二比重過高 ({ratio_leveraged:.1f}%)**：股市大漲，建議賣出部分正二轉入 00865B 鎖定獲利。"
        else:
            suggestion = f"📉 **正二比重過低 ({ratio_leveraged:.1f}%)**：股市大跌，建議賣出部分 00865B 加碼正二抄底！"
    else:
        title = "📊 **【每日資產定時簡報】資產比例健康**"
        suggestion = "✅ **比例維持正常**（正二維持在 75% ~ 85% 之間），無需執行再平衡。"

    # 組合完整推播訊息
    message = (
        f"{title}\n"
        f"- **總資產市值**：${total_val:,.0f} TWD\n"
        f"- **今日資產損益**：`{pnl_str}`\n"
        f"- **正二總市值**：${val_leveraged:,.0f} ({ratio_leveraged:.1f}%)\n"
        f"- **短債總市值**：${val_bond:,.0f} ({ratio_bond:.1f}%)\n\n"
        f"{suggestion}"
    )

    # 發送簡報訊息到 Discord
    send_discord_message(message)
    print("訊息處理完成並已發送")

if __name__ == "__main__":
    main()
