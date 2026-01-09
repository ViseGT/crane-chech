import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ==========================================
#              1. 基礎設定
# ==========================================
st.set_page_config(page_title="起重機作業前自檢表", layout="centered")

# ==========================================
#              2. CSS 樣式 (維持不變)
# ==========================================
st.markdown("""
    <style>
    /* 隱藏選單 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    html, body, [class*="css"]  {
        font-family: "Microsoft JhengHei", sans-serif;
    }

    /* 題目區塊 */
    .question-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 10px;
        border: 2px solid #e0e0e0;
    }
    .question-text {
        font-size: 22px !important;
        font-weight: 900;
        color: #1f1f1f;
        line-height: 1.4;
    }

    /* 按鈕樣式 (primary=綠色, secondary=紅色) */
    button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        height: 80px !important;
        font-size: 26px !important;
        font-weight: bold !important;
    }
    button[kind="primary"]:active {
        background-color: #1e7e34 !important;
    }

    button[kind="secondary"] {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
        height: 80px !important;
        font-size: 26px !important;
        font-weight: bold !important;
    }
    button[kind="secondary"]:active {
        background-color: #bd2130 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
#              3. 題目資料
# ==========================================
QUESTIONS = [
    {"text": "1. 吊掛鉤頭插銷功能是否正常？", "image": "1.jpg"},
    {"text": "2. 吊鉤防滑舌片是否無變形？", "image": "2.jpg"},
]

# ==========================================
#              4. 邏輯初始化
# ==========================================
def init_state():
    # 預設狀態是 'login'
    if 'step' not in st.session_state: st.session_state.step = 'login'
    if 'user_name' not in st.session_state: st.session_state.user_name = ""
    if 'current_q_index' not in st.session_state: st.session_state.current_q_index = 0
    if 'answers' not in st.session_state: st.session_state.answers = []

def record_answer(answer_text):
    current_q_data = QUESTIONS[st.session_state.current_q_index]
    status = "✅" if answer_text == "是" else "❌"
    
    st.session_state.answers.append({
        "題目": current_q_data["text"],
        "您的回答": answer_text,
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
#              5. 頁面顯示流程 (State Machine)
# ==========================================

# 🟥 階段 1：登入頁面
# 只有當 step 等於 'login' 時，這裡的程式碼才會執行
# 一旦切換到 'quiz'，這裡包含「按鈕」的所有東西都會被跳過（也就是隱藏）
if st.session_state.step == 'login':
    st.title("🏗️ 起重機作業前自檢")
    st.write("")
    
    with st.container():
        st.info("請輸入檢查人員姓名")
        name_input = st.text_input("姓名", value=st.session_state.user_name)
        st.write("")
        
        # 這裡的按鈕只存在於 Login 階段
        if st.button("開始檢查", type="primary", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input
                # 關鍵動作：切換狀態
                st.session_state.step = 'quiz'
                # 關鍵動作：強制重新整理頁面
                st.rerun()
            else:
                st.error("請輸入姓名")

# 🟨 階段 2：答題頁面
# 當 step 變成 'quiz' 後，程式會直接跳來這裡執行
elif st.session_state.step == 'quiz':
    p = (st.session_state.current_q_index + 1) / len(QUESTIONS)
    st.progress(p)
    
    q_data = QUESTIONS[st.session_state.current_q_index]
    
    st.markdown(f'''
        <div class="question-box">
            <div class="question-text">{q_data["text"]}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    if q_data["image"] and os.path.exists(q_data["image"]):
        st.image(q_data["image"], use_container_width=True)
    
    st.write("")
    
    c1, c2 = st.columns(2, gap="small")
    idx = st.session_state.current_q_index
    
    with c1:
        if st.button("是 (正常)", key=f"yes_{idx}", type="primary"):
            record_answer("是")
            
    with c2:
        if st.button("否 (異常)", key=f"no_{idx}", type="secondary"):
            record_answer("否")

# 🟩 階段 3：結果頁面
elif st.session_state.step == 'result':
    st.title("📋 檢查結果")
    st.success(f"檢查員：{st.session_state.user_name}")
    
    df = pd.DataFrame(st.session_state.answers)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if any(x['您的回答'] == "否" for x in st.session_state.answers):
        st.error("⛔ 結果：不合格 (請改善)")
    else:
        st.balloons()
        st.success("✅ 結果：合格 (可作業)")
        
    st.write("")
    if st.button("🔄 返回首頁", type="primary", use_container_width=True):
        restart()


