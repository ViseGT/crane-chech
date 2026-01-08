import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
#              1. 基礎設定
# ==========================================
st.set_page_config(page_title="起重機作業前自檢表", layout="centered")

# ==========================================
#              2. CSS 樣式優化 (手機專用)
# ==========================================
st.markdown("""
    <style>
    /* 隱藏預設的 Hamburger Menu 和 Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 全域字體加大 */
    html, body, [class*="css"]  {
        font-family: "Microsoft JhengHei", sans-serif;
    }
    
    /* 題目文字樣式 */
    .question-text {
        font-size: 28px !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
        line-height: 1.5;
        color: #333;
    }

    /* 按鈕容器樣式 */
    .stButton button {
        width: 100%;
        height: 100px; /* 按鈕高度，方便手指點擊 */
        font-size: 32px !important;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        color: white;
    }

    /* 左邊按鈕 (綠色 - 代表有/正常) */
    div[data-testid="column"]:nth-of-type(1) .stButton button {
        background-color: #28a745 !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
    }
    div[data-testid="column"]:nth-of-type(1) .stButton button:active {
        background-color: #1e7e34 !important;
    }

    /* 右邊按鈕 (紅色 - 代表沒有/異常) */
    div[data-testid="column"]:nth-of-type(2) .stButton button {
        background-color: #dc3545 !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.2);
    }
    div[data-testid="column"]:nth-of-type(2) .stButton button:active {
        background-color: #bd2130 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
#              3. 題目資料 (已更新)
# ==========================================
# 您可以隨時在此區塊新增或修改題目
QUESTIONS = [
    "1. 外伸撐座是否「完全伸展」？",  # <--- 已為您加入這題
    "2. 過捲預防裝置是否功能正常？",
    "3. 吊鉤防滑舌片是否無變形？",
    "4. 吊掛索具是否無斷絲、斷股？",
    "5. 作業範圍內是否已完成人員淨空？",
    "6. 吊掛作業是否由合格吊掛手指揮？"
]

# ==========================================
#              4. 邏輯函數
# ==========================================

def init_state():
    if 'step' not in st.session_state: st.session_state.step = 'login'
    if 'user_name' not in st.session_state: st.session_state.user_name = ""
    if 'current_q_index' not in st.session_state: st.session_state.current_q_index = 0
    if 'answers' not in st.session_state: st.session_state.answers = []

def record_answer(answer_text):
    """記錄答案並跳下一題"""
    current_q = QUESTIONS[st.session_state.current_q_index]
    
    # 判斷狀態：如果是「沒有」，標記為異常(❌)
    status = "✅" if answer_text == "有" else "❌"
    
    st.session_state.answers.append({
        "題目": current_q,
        "您的回答": answer_text, # 記錄有或沒有
        "狀態": status 
    })
    
    if st.session_state.current_q_index < len(QUESTIONS) - 1:
        st.session_state.current_q_index += 1
    else:
        st.session_state.step = 'result'
    
    st.rerun()

def restart():
    st.session_state.current_q_index = 0
    st.session_state.answers = []
    st.session_state.step = 'login'
    st.rerun()

init_state()

# ==========================================
#              5. 頁面顯示邏輯
# ==========================================

# --- 頁面 1: 登入 ---
if st.session_state.step == 'login':
    st.title("🏗️ 起重機作業前自檢")
    st.info("請輸入檢查人員姓名以開始作業")
    
    name_input = st.text_input("檢查人員姓名 (必填)", value=st.session_state.user_name)
    
    if st.button("開始檢查 ➡️", type="primary", use_container_width=True):
        if name_input.strip():
            st.session_state.user_name = name_input
            st.session_state.step = 'quiz'
            st.rerun()
        else:
            st.error("⚠️ 請務必輸入姓名！")

# --- 頁面 2: 檢查過程 ---
elif st.session_state.step == 'quiz':
    progress = (st.session_state.current_q_index + 1) / len(QUESTIONS)
    st.progress(progress)
    st.caption(f"檢查進度: {st.session_state.current_q_index + 1} / {len(QUESTIONS)}")
    
    q_text = QUESTIONS[st.session_state.current_q_index]
    st.markdown(f'<div class="question-text">{q_text}</div>', unsafe_allow_html=True)
    
    st.write("") 
    st.write("")
    
    c1, c2 = st.columns(2, gap="medium")
    
    with c1:
        # 左邊按鈕：有
        if st.button("有", key="btn_yes"):
            record_answer("有")
            
    with c2:
        # 右邊按鈕：沒有
        if st.button("沒有", key="btn_no"):
            record_answer("沒有")

# --- 頁面 3: 結果總覽 ---
elif st.session_state.step == 'result':
    st.title("📋 檢查結果報告")
    
    st.markdown(f"**檢查人員：** {st.session_state.user_name}")
    st.markdown(f"**檢查時間：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")
    
    df = pd.DataFrame(st.session_state.answers)
    st.table(df)
    
    # 判斷是否所有題目都回答「有」
    # 邏輯：如果有任何一題回答「沒有」，則視為不通過
    has_error = any(x['您的回答'] == "沒有" for x in st.session_state.answers)
    
    if has_error:
        st.error("⛔ 檢查未通過！請立即改善缺失項目。")
    else:
        st.success("✅ 檢查通過！可以開始作業。")
        
    st.markdown("---")
    if st.button("🔄 結束並返回首頁", use_container_width=True):
        restart()
