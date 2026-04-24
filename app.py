import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 設定頁面 ---
st.set_page_config(page_title="台南綠園道民調系統", page_icon="🌳", layout="centered")

# --- 數據檔案路徑 ---
DATA_FILE = "survey_responses.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['privacy', 'thermal', 'effort', 'shading', 'neighbor'])

def save_data(new_row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- 側邊欄選單 ---
menu = st.sidebar.selectbox("選單", ["民眾問卷填寫", "管理員數據中心"])

# --- 頁面 1: 民眾問卷填寫 ---
if menu == "民眾問卷填寫":
    st.title("🌳 台南綠園道民意調查")
    st.write("您的每一分意見，都是塑造未來城市綠帶的重要參考。")
    
    with st.form("survey_form", clear_on_submit=True):
        st.subheader("1. 隱私 vs. 視野")
        privacy = st.select_slider("水平距離多近你會開始感到不安？", options=list(range(3, 31)), value=15)
        st.caption("3公尺 (不安) ←----------------→ 30公尺 (無感)")
        
        st.subheader("2. 體感溫度 vs. 壓迫")
        thermal = st.slider("願意接受多少結構體遮蔽天空？", 0, 100, 50)
        st.caption("0% (曬太陽) ←----------------→ 100% (全遮)")
        
        st.subheader("3. 坡度 vs. 安全")
        effort = st.slider("願意爬多長的坡來換取交通安全？", 0, 100, 50)
        st.caption("0公尺 (不爬) ←----------------→ 100公尺 (願爬)")
        
        st.subheader("4. 遮蔭 vs. 安全")
        shading = st.slider("犧牲多少白天遮蔭換取夜間通透？", 0, 100, 50)
        st.caption("0% (全遮) ←----------------→ 100% (無遮)")
        
        st.subheader("5. 鄰里隱私 (隔音牆)")
        neighbor = st.slider("對保護隱私用的隔音牆接受度？", 0, 100, 50)
        st.caption("0% (不接受) ←----------------→ 100% (支持)")
        
        submitted = st.form_submit_button("提交我的意見", use_container_width=True)
        
        if submitted:
            new_data = {
                'privacy': privacy, 'thermal': thermal, 'effort': effort, 
                'shading': shading, 'neighbor': neighbor
            }
            save_data(new_data)
            st.success("✅ 提交成功！感謝您的參與。")
            st.balloons()

# --- 頁面 2: 管理員數據中心 ---
elif menu == "管理員數據中心":
    st.title("📊 雲端即時統計中心")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        password = st.text_input("請輸入管理員密碼", type="password")
        if st.button("登入後台", use_container_width=True):
            if password == "tainan2024":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("密碼錯誤")
    else:
        st.sidebar.button("登出管理員", on_click=lambda: st.session_state.update({"logged_in": False}))
        
        df = load_data()
        
        if df.empty:
            st.warning("目前尚無蒐集到的資料。")
        else:
            # --- 綜合結果統計 ---
            col1, col2, col3 = st.columns(3)
            
            # 簡易判定：平均 > 50 算同意
            df_numeric = df.apply(pd.to_numeric, errors='coerce')
            df['avg_score'] = df_numeric.mean(axis=1)
            agree_count = len(df[df['avg_score'] >= 50])
            disagree_count = len(df) - agree_count
            
            col1.metric("累積樣本數", f"{len(df)} 份")
            col2.metric("總體同意", f"{agree_count} 份")
            col3.metric("總體不同意", f"{disagree_count} 份")
            
            # --- 圖表展示 ---
            st.divider()
            st.subheader("各維度平均接受度 (%)")
            avg_data = df_numeric.drop(columns=['avg_score'], errors='ignore').mean().reset_index()
            avg_data.columns = ['維度', '平均百分比']
            
            fig = px.bar(avg_data, x='維度', y='平均百分比', color='平均百分比', 
                         color_continuous_scale='Greens', range_y=[0, 100])
            st.plotly_chart(fig, use_container_width=True)
            
            # --- 資料下載 ---
            st.download_button("下載原始數據 (CSV)", df.to_csv(index=False), "survey_results.csv", "text/csv")
            
            # --- 清除資料 ---
            if st.button("⚠️ 清除所有蒐集資料"):
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                st.success("資料已清空！")
                st.rerun()

# --- 自動 QR Code 分享功能 (側邊欄) ---
st.sidebar.divider()
st.sidebar.markdown("### 📱 分享問卷")
st.sidebar.write("掃描下方 QRCode 即可填寫：")
# 使用圖片 API 生成 QRCode
st.sidebar.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://bibibo-ceup2svsqq2kju7jjj2hvz.streamlit.app/&color=1a5d1a")
