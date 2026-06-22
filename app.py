import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# 1. 網頁基本設定
st.set_page_config(page_title="硬體市場價格波動追蹤系統", layout="wide")
st.title("💻 電腦硬體市場價格波動儀表板 ")
st.markdown("請在左側輸入想查詢的硬體名稱，系統會自動生成對應的歷史價格趨勢。 (示範版本：使用模擬數據)")

# 2. 側邊欄：讓使用者自己輸入文字
st.sidebar.header("⚙️ 搜尋設定")
st.sidebar.markdown("您可以一次查詢多個硬體，請用**半形逗號 (,)** 分隔。")

# 使用 text_input 讓使用者打字，並給一個預設值
user_input = st.sidebar.text_input(
    "請輸入想查詢的硬體：",
    value="RTX 4090, Intel i9-14900K, 1TB SSD"
)

# 處理使用者的輸入：用逗號切開，並清掉多餘的空白
if user_input:
    # 這裡用到 Python 的 List Comprehension 語法
    selected_hardware = [hw.strip() for hw in user_input.split(",") if hw.strip() != ""]
else:
    selected_hardware = []

# 3. 根據使用者輸入的清單「動態」生成模擬數據
@st.cache_data
def generate_dynamic_data(hardware_list):
    if not hardware_list:
        return pd.DataFrame()
        
    dates = [datetime.today() - timedelta(days=i) for i in range(180)]
    dates.reverse()
    data = {"日期": dates}
    
    # 針對使用者輸入的每一個硬體，自動生出一組價格
    for hw in hardware_list:
        # 為了讓同一個名字每次算出來的模擬價格都一樣，我們用名字當作隨機種子
        random.seed(hw) 
        base_price = random.randint(3000, 40000) # 隨機決定一個 3000~40000 的基準價
        
        # 模擬價格波動 (微幅下跌趨勢加上每日隨機震盪)
        data[hw] = np.linspace(base_price, base_price * 0.9, 180) + np.random.normal(0, base_price * 0.02, 180)
        
    return pd.DataFrame(data)

# 將整理好的使用者清單，丟進函數裡產生資料庫
df = generate_dynamic_data(selected_hardware)

# 4. 主畫面：數據分析與視覺化
if selected_hardware:
    st.subheader("📊 關鍵價格指標")
    
    # 動態產生 Metric 欄位
    cols = st.columns(len(selected_hardware))
    for i, hw in enumerate(selected_hardware):
        max_price = df[hw].max()
        min_price = df[hw].min()
        current_price = df[hw].iloc[-1]
        
        # 計算跌幅或漲幅
        price_change = current_price - max_price
        drop_percent = (price_change / max_price) * 100
        
        with cols[i]:
            st.metric(
                label=f"{hw} (目前價格)",
                value=f"NT$ {int(current_price):,}",
                delta=f"{drop_percent:.2f}% (距半年高點)",
                delta_color="inverse"
            )
            st.caption(f"📈 最高: NT$ {int(max_price):,} | 📉 最低: NT$ {int(min_price):,}")

    st.divider()
    
    # 繪製價格趨勢折線圖
    st.subheader("📈 歷史價格趨勢圖")
    chart_data = df.set_index("日期")[selected_hardware]
    st.line_chart(chart_data)
    
else:
    st.warning("👈 請從左側輸入至少一項硬體名稱來顯示數據。")