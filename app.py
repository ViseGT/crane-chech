import streamlit as st
import pandas as pd
from datetime import datetime
import os
# ==========================================
#              1. 基礎設定
# ==========================================
st.set_page_config(page_title="起重機作業前自檢表", layout="centered")
# ==========================================
#              2. CSS 樣式
# ==========================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    html, body, [class*="css"]  {
        font-family: "Microsoft JhengHei", sans-serif;
    }

    .question-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 15px;
        border: 2px solid #e0e0e0;
    }
    .question-text {
        font-size: 22px !important;
        font-weight: 900;
        color: #1f1f1f;
        line-height: 1.4;
    }
    
    /* 按鈕樣式 */
    button[kind="secondary"], button[kind="primary"] {
        height: 80px !important;
        width: 100% !important;
        font-size: 26px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
    }

    /* 左邊按鈕 (綠色) */
    [data-testid="column"]:nth-of-type(1) button {
        background-color: #28a745 !important;
        color: white !important;
    }
    [data-testid="column"]:nth-of-type(1) button:active {
        background-color: #1e7e34 !important;
        transform: scale(0.98);
    }

    /* 右邊按鈕 (紅色) */
    [data-testid="column"]:nth-of-type(2) button {
        background-color: #dc3545 !important;
        color: white !important;
    }
    [data-testid="column"]:nth-of-type(2) button:active {
        background-color: #bd2130 !important;
        transform: scale(0.98);
    }
    </style>
""", unsafe_allow_html=True)
# ==========================================
#              3. 題目資料 (加上圖片設定)
# ==========================================
# 格式說明：
# "text": "題目文字"
# "image": "您上傳的圖片檔名" (如果沒有圖，就填 None)

QUESTIONS = [
    {
        "text": "1. 吊掛鉤頭插銷功能是否正常？", 
        "image": "1.jpg"  # 請確保 GitHub 有上傳名為 1.jpg 的檔案
    },
    {
        "text": "2. 吊鉤防滑舌片是否無變形？", 
        "image": "2.jpg"  # 請確保 GitHub 有上傳名為 2.jpg 的檔案
    },
    {
        "text": "3. 過捲預防裝置是否功能正常？", 
        "image": None     # 這一題沒有圖片，填 None
    },
    {
        "text": "4. 吊掛索具是否無斷絲、斷股？", 
        "image": None
    },
    {
        "text": "5. 作業範圍內是否已完成人員淨空？", 
        "image": None
    },
    {
        "text": "6. 吊掛作業是否由合格吊掛手指揮？", 
        "image": None
    }
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
    current_q_data = QUESTIONS[st.session_state.current_q_index]
    status = "✅" if answer_text == "否" else "❌"

    st.session_state.answers.append({
        "題目": current_q_data["text"], # 只存文字，不存圖片路徑
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
#              5. 頁面顯示
# ==========================================

# --- 頁面 1: 登入 ---
if st.session_state.step == 'login':
    st.title("🏗️ 起重機作業前自檢")
    st.write("")

with st.container():
        st.info("請輸入檢查人員姓名")
        name_input = st.text_input("姓名", value=st.session_state.user_name)
        st.write("")

if st.button("開始檢查 ➡️", type="primary", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input
                st.session_state.step = 'quiz'
                st.rerun()
            else:
                st.error("⚠️ 請輸入姓名")

# --- 頁面 2: 答題 (顯示圖片核心區) ---
elif st.session_state.step == 'quiz':
    p = (st.session_state.current_q_index + 1) / len(QUESTIONS)
    st.progress(p)

# 取得當前題目的資料 (包含文字和圖片)
    q_data = QUESTIONS[st.session_state.current_q_index]
    
    # 1. 顯示題目文字
    st.markdown(f'''
    <div class="question-box">
            <div class="question-text">{q_data["text"]}</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # 2. 顯示圖片 (如果有設定的話)
    if q_data["image"]:
        # 檢查檔案是否存在，避免報錯
        if os.path.exists(q_data["image"]):
            st.image(q_data["image"], use_container_width=True)
        else:
            # 如果找不到圖片，顯示提示 (僅測試用，正式上線可拿掉)
            st.warning(f"找不到圖片: {q_data['image']}，請確認 GitHub 是否已上傳。")
    
    st.write("")

# 按鈕區
    c1, c2 = st.columns(2, gap="small")
    idx = st.session_state.current_q_index
    
    with c1:
        if st.button("是 (正常)", key=f"yes_{idx}"):
            record_answer("是")

    with c2:
        if st.button("否 (異常)", key=f"no_{idx}"):
            record_answer("否")

# --- 頁面 3: 結果 ---
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
















