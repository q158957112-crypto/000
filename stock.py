import os
import requests

# 取得 Discord Webhook 網址
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def check_and_send_alert():
    # ==========================================
    # 1. 數據與資產配置設定 (目標 7 : 3)
    # ==========================================
    total_assets = 2175756      # 總資產市值 (TWD)
    today_pnl = -29376          # 今日損益 (TWD)
    drop_percentage = 3.5       # 今日跌幅百分比（正數代表下跌幅度）

    # 各標的佔比數據（將 00631L 與 00685L 加在一起計算）
    ratio_00631L = 45.0         # 00631L 佔比 %
    ratio_00685L = 25.0         # 00685L 佔比 %
    leverage_2x_ratio = ratio_00631L + ratio_00685L  # 正二總計 (00631L + 00685L) = 70%
    
    bond_cash_ratio = 30.0      # 債券與現金總和佔比 %

    # 目標比例
    target_leverage = 70.0
    target_bond_cash = 30.0

    # 計算偏離幅度
    diff_leverage = round(leverage_2x_ratio - target_leverage, 1)

    # 偏離提示訊息
    if abs(diff_leverage) >= 5.0:
        rebalance_advice = f"⚠️ **注意**：正二組合比例已偏離目標 ({diff_leverage:+}%)，建議進行再平衡！"
    else:
        rebalance_advice = "✅ **資產比例正常**：維持在目標 7:3 附近。"

    # ==========================================
    # 2. 組合 Discord 推播內容
    # ==========================================
    message = (
        f"🚨 **[盤中警報] 發現資產跌幅達 {drop_percentage}%！**\n"
        f"• **總資產市值**：${total_assets:,} TWD\n"
        f"• **今日資產損益**：${today_pnl:,} TWD (**-{drop_percentage}%**)\n\n"
        f"📊 **目前資產配置 (目標 7:3)**：\n"
        f"• **正二總計 (00631L + 00685L)**：{leverage_2x_ratio}% (目標 {target_leverage}%)\n"
        f"  - 00631L：{ratio_00631L}%\n"
        f"  - 00685L：{ratio_00685L}%\n"
        f"• **債券與現金**：{bond_cash_ratio}% (目標 {target_bond_cash}%)\n"
        f"• **狀態**：{rebalance_advice}"
    )

    if not WEBHOOK_URL:
        print("未設定 webhook，訊息內容如下：")
        print(message)
        return

    # ==========================================
    # 3. 觸發條件判斷（跌幅 >= 2% 才發送）
    # ==========================================
    if drop_percentage >= 2.0:
        payload = {"content": message}
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print("跌幅已達 2% 以上，正二組合比例警報已成功發送至 Discord！")
        else:
            print(f"發送失敗，HTTP 狀態碼: {response.status_code}")
    else:
        print(f"目前跌幅為 {drop_percentage}%，未達 2% 門檻，暫不發送通知。")

if __name__ == "__main__":
    check_and_send_alert()
