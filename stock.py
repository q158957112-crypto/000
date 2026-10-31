import requests
import json

# 1. 設定你關注的槓桿 ETF 清單
my_stocks = ["00631L.TW", "00685L.TW"]

# 2. 設定警示門檻（可以分別控制漲跌）
drop_threshold = -2.0   # 跌幅達到 -2.0%（含）以上時發送警報
rise_threshold = 2.0    # 漲幅達到 +2.0%（含）以上時發送警報

# 3. 填入你的 Discord Webhook 網址（保留雙引號）
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1566002402669240434/O35y8OBwaZ2ZdGgJjx0r-h_4Vxx3639z6mWxlUZU_KmeS5977j6vkJOHwRk6J_-c1Elr"

def send_discord_webhook(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    return response.status_code

print("正在檢查 00631L 與 00685L 的市場表現...\n")

alert_messages = []

for code in my_stocks:
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{code}?range=1mo&interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        
        result = data['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        
        valid_closes = [c for c in closes if c is not None]
        
        if len(valid_closes) < 2:
            print(f"⚠️ 代號 {code} 的有效價格資料不足。\n")
            continue
            
        latest_close = float(valid_closes[-1])
        prev_close = float(valid_closes[-2])
        
        daily_return = ((latest_close - prev_close) / prev_close) * 100
        
        print(f"📌 股票代號：{code}")
        print(f"   - 最新收盤價：{latest_close:.2f}")
        print(f"   - 今日漲跌幅：{daily_return:.2f}%")
        
        # 檢查是否觸發跌幅警報
        if daily_return <= drop_threshold:
            msg = f"🚨 **【槓桿 ETF 跌幅警示】**\n代號：`{code}`\n今日跌幅：**{daily_return:.2f}%**\n最新收盤價：`{latest_close:.2f}`"
            alert_messages.append(msg)
            
        # 檢查是否觸發漲幅警報
        elif daily_return >= rise_threshold:
            msg = f"🚀 **【槓桿 ETF 漲幅警示】**\n代號：`{code}`\n今日漲幅：**+{daily_return:.2f}%**\n最新收盤價：`{latest_close:.2f}`"
            alert_messages.append(msg)
            
    except Exception as e:
        print(f"處理 {code} 時發生錯誤：{e}\n")

if len(alert_messages) > 0:
    full_message = "\n\n".join(alert_messages)
    send_discord_webhook(full_message)
    print("\n📲 成功透過 Discord 發送行情警示通知！")
else:
    print("\n✅ 今日所有追蹤標的皆未達到漲跌幅門檻。")

# 防止畫面閃退的暫停指令
input("\n測試結束！請按下 Enter 鍵關閉視窗...")
