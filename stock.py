import os
import requests

# 取得 Discord Webhook 網址
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check_and_send_alert():
    # 1. 這裡放入你的實際抓取或計算數據邏輯
    total_assets = 2175756  # 總資產
    today_pnl = -29376      # 今日損益
    drop_percentage = 3.5   # 今日跌幅百分比（正數代表下跌幅度）

    # 組合要發送的訊息內容
    message = (
        "🚨 **[盤中警報] 發現資產跌幅超過 2%！**\n"
        f"• **總資產市值**：${total_assets:,} TWD\n"
        f"• **今日資產損益**：${today_pnl:,} TWD (**-{drop_percentage}%**)\n"
        "• **建議**：目前跌幅已達警戒線，請密切關注市場波動！"
    )

    if not WEBHOOK_URL:
        print("未設定 webhook，訊息內容如下：")
        print(message)
        return

    # 2. 判斷是否達到 2% 的跌幅門檻
    if drop_percentage >= 2.0:
        payload = {"content": message}
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("跌幅已達 2% 以上，警報已成功發送至 Discord！")
        else:
            print(f"發送失敗，HTTP 狀態碼: {response.status_code}")
    else:
        print(f"目前跌幅為 {drop_percentage}%，未達 2% 門檻，暫不發送通知。")

if __name__ == "__main__":
    check_and_send_alert()
