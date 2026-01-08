import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
#              1. 基礎設定
# ==========================================
st.set_page_config(page_title="起重機作業前自檢表", layout="centered")

# ==========================================
#              2. CSS 樣式優化 (修復按鈕消失問題)
# ==========================================
st.markdown("""
    <style>
    /* 隱藏預設選單 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 全域字體 */
    html, body, [class*="css"]  {
        font-family: "Microsoft JhengHei", sans-serif;
    }
    
    /* 題目文字樣式 */
    .question-text {
        font-size: 26px !important;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        line-height: 1.5;
        color: #333;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 10px;
    }

    /* 按鈕基礎樣式 (預設黑字，避免白底白字看不見) */
    .stButton button {
        width: 100%;
        height: 90px;
        font-size: 28px !important;
        font-weight: bold;
        border-radius: 12px;
        border: 2px solid #ddd; /* 加個邊框確保可見 */
        color: #333; /* 預設文字黑色 */
        transition: all 0.2s;
    }

    /* 左邊按鈕 (綠色) */
    div[data-testid="column"]:nth-of-type(1) .stButton button {
        background-color: #28a745 !important;
        border-color: #28a745 !important;
        color: white !important; /* 背景成功變綠才變白字 */
    }
    
    /* 右邊按鈕 (紅色) */
    div[data-testid="column"]:nth-of-type(2) .stButton button {
        background-color: #dc3545 !important;
        border-color: #dc3545 !important;
        color: white !important; /* 背景成功變紅才變白字 */
    }

    /* 按下時的效果 */
    div[data-testid="column"] .stButton button:active {
        transform: scale(0.98);
        opacity: 0.9;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
#              3. 題目資料
# ==========================================
QUESTIONS = [
    "1. 外伸撐座是否「完全伸展」？",
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
    status = "✅" if answer_text == "有" else "❌"
    
    st.session_state.answers.append({
        "題目": current_q,
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
#              5. 頁面顯示邏輯
# ==========================================

# --- 頁面 1: 登入 ---
if st.session_state.step == 'login':
    st.title("🏗️ 起重機作業前自檢")
    
    with st.container():
        st.markdown("### 👷 請輸入檢查人員資料")
        name_input = st.text_input("姓名 (必填)", value=st.session_state.user_name)
        
        st.write("") # 空格
        
        if st.button("開始檢查 ➡️", type="primary", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input
                st.session_state.step = 'quiz'
                st.rerun()
            else:
                st.error("⚠️ 請輸入姓名才能開始！")

# --- 頁面 2: 檢查過程 ---
elif st.session_state.step == 'quiz':
    # 進度條
    progress = (st.session_state.current_q_index + 1) / len(QUESTIONS)
    st.progress(progress)
    st.caption(f"進度: {st.session_state.current_q_index + 1} / {len(QUESTIONS)}")
    
    # 顯示題目
    q_text = QUESTIONS[st.session_state.current_q_index]
    st.markdown(f'<div class="question-text">{q_text}</div>', unsafe_allow_html=True)
    
    st.write("") 
    st.write("") # 增加間距
    
    # 建立兩欄
    c1, c2 = st.columns(2, gap="small")
    
    # 為了避免按鈕消失或重複，我們給每個按鈕一個隨題號變化的 key
    idx = st.session_state.current_q_index
    
    with c1:
        # 左邊按鈕
        if st.button("有", key=f"yes_{idx}"):
            record_answer("有")
            
    with c2:
        # 右邊按鈕
        if st.button("沒有", key=f"no_{idx}"):
            record_answer("沒有")

# --- 頁面 3: 結果總覽 ---
elif st.session_state.step == 'result':
    st.title("📋 檢查結果報告")
    
    st.info(f"👤 檢查人員：{st.session_state.user_name}")
    st.caption(f"🕒 時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 顯示結果表格
    df = pd.DataFrame(st.session_state.answers)
    st.table(df)
    
    # 判斷結果
    has_error = any(x['您的回答'] == "沒有" for x in st.session_state.answers)
    
    if has_error:
        st.error("⛔ 檢查未通過！請立即改善缺失項目。")
    else:
        st.success("✅ 檢查通過！可以開始作業。")
        
    st.markdown("---")
    if st.button("🔄 返回首頁", use_container_width=True):
        restart()
