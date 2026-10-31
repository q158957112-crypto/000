import os
import requests

# 取得 Discord Webhook 網址
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check_and_send_alert():
    # ==========================================
    # 1. 在這裡計算你的資產、損益與各持股比例
    # ==========================================
    total_assets = 2175756      # 總資產市值 (TWD)
    today_pnl = -29376          # 今日損益 (TWD)
    drop_percentage = 3.5       # 今日跌幅百分比（正數代表下跌幅度）

    # 範例：各持股/資產的佔比數據（請對應你原本的計算結果）
    asset_ratios = {
        "00631L": 45.2,
        "00685L": 35.1,
        "現金/其他": 19.7
    }

    # ==========================================
    # 2. 組合要發送的 Discord 訊息內容
    # ==========================================
    ratio_text = "\n".join([f"• **{name}**：{ratio}%" for name, ratio in asset_ratios.items()])

    # 基本日報/警報內容
    message = (
        f"🚨 **[盤中警報] 發現資產跌幅達 {drop_percentage}%！**\n"
        f"• **總資產市值**：${total_assets:,} TWD\n"
        f"• **今日資產損益**：${today_pnl:,} TWD (**-{drop_percentage}%**)\n\n"
        f"📊 **目前資產配置比例**：\n{ratio_text}\n"
        "• **建議**：跌幅已達 2% 警戒線，請密切關注市場波動！"
    )

    if not WEBHOOK_URL:
        print("未設定 webhook，訊息內容如下：")
        print(message)
        return

    # ==========================================
    # 3. 判斷是否達到 2% 的跌幅門檻
    # ==========================================
    if drop_percentage >= 2.0:
        payload = {"content": message}
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("跌幅已達 2% 以上，包含比例的警報已成功發送至 Discord！")
        else:
            print(f"發送失敗，HTTP 狀態碼: {response.status_code}")
    else:
        print(f"目前跌幅為 {drop_percentage}%，未達 2% 門檻，暫不發送通知。")

if __name__ == "__main__":
    check_and_send_alert()
