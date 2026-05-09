import streamlit as st
import json
import os
import base64
import calendar
from datetime import date
from io import BytesIO
from PIL import Image

# --- 定数・設定 ---
DB_FILE = "data.json"
MBTI_LIST = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
STATUS_EMOJIS = {"最高！": "😆", "まったり": "☕", "お疲れ": "🔋", "ぴえん": "🥺", "そっとして": "💤", "激おこ": "💢"}

# --- スタイル設定（ピンク×白・入力欄ホワイトアウト） ---
def apply_custom_style():
    st.markdown("""
        <style>
        .stApp { background-color: #fff0f5 !important; }
        
        /* 入力欄を真っ白に */
        div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div {
            background-image: none !important;
            background-color: #ffffff !important;
            background: #ffffff !important;
            border: 2px solid #ffb6c1 !important;
        }
        input, textarea, select {
            background-color: #ffffff !important;
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }

        /* ボタンデザイン */
        .stButton > button {
            background-color: #ffffff !important;
            color: #ff69b4 !important;
            border: 2px solid #ff69b4 !important;
            font-weight: bold !important;
            border-radius: 10px !important;
        }

        /* テキスト色固定 */
        label, p, h1, h2, h3, h4, span, .stMarkdown {
            color: #222222 !important;
            font-weight: bold !important;
        }
        
        /* 記念日カウンターのスタイル */
        .anniversary-box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 20px;
            border: 3px solid #ffb6c1;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 基本機能 ---
def load_data():
    default = {"first_meet": "2026-01-22", "profiles": {}, "memories": [], "events": [], "status": {"user1": {"name": "1人目", "mood": "まったり"}, "user2": {"name": "2人目", "mood": "まったり"}}}
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                for k,v in default.items():
                    if k not in d: d[k] = v
                return d
        except: return default
    return default

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def image_to_base64(img):
    buf = BytesIO()
    img.thumbnail((800, 800))
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode()

data = load_data()
st.set_page_config(page_title="仲好子", page_icon="💖", layout="wide")
apply_custom_style()

tabs = st.tabs(["🏠 ホーム", "❤️ 相性", "👤 プロフ", "📸 アルバム", "📅 予定", "🛡️ 設定"])

# 1. ホーム
with tabs[0]:
    st.title("💖 二人のいま")
    
    # --- 日数カウント表示 ---
    first_date = date.fromisoformat(data["first_meet"])
    today = date.today()
    days_passed = (today - first_date).days
    
    st.markdown(f"""
        <div class="anniversary-box">
            <h3 style="margin:0; color:#ff69b4;">出会ってから</h3>
            <h1 style="margin:0; font-size:4rem; color:#ff1493;">{days_passed} 日</h1>
            <p style="margin:0; color:#ffb6c1;">since {data['first_meet']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, k in enumerate(["user1", "user2"]):
        u = data["status"][k]
        with cols[i]:
            st.markdown(f"### {u['name']}")
            st.markdown(f"<h1 style='text-align:center;'>{STATUS_EMOJIS.get(u['mood'], '💖')}</h1>", unsafe_allow_html=True)
            nm = st.selectbox(f"気分変更", list(STATUS_EMOJIS.keys()), key=f"hm_{k}", index=list(STATUS_EMOJIS.keys()).index(u["mood"]) if u["mood"] in STATUS_EMOJIS else 1)
            if st.button(f"更新する", key=f"hb_{k}"):
                data["status"][k]["mood"] = nm; save_data(data); st.rerun()

# 3. プロフィール（名前・詳細設定）
with tabs[2]:
    st.header("👤 プロフィール設定")
    p_cols = st.columns(2)
    for i, k in enumerate(["user1", "user2"]):
        with p_cols[i]:
            cn = data["status"][k]["name"]
            ex = data["profiles"].get(cn, {})
            st.subheader(f"{cn} のプロフ")
            n = st.text_input("名前", value=cn, key=f"p_n_{i}")
            bd = st.text_input("誕生日", value=ex.get("birthday", ""), key=f"p_bd_{i}")
            jb = st.text_input("職業", value=ex.get("job", ""), key=f"p_j_{i}")
            hb = st.text_input("趣味", value=ex.get("hobby", ""), key=f"p_h_{i}")
            m = st.selectbox("MBTI", MBTI_LIST, key=f"p_m_{i}", index=MBTI_LIST.index(ex.get("mbti", "INFP")) if ex.get("mbti") in MBTI_LIST else 5)
            f = st.text_input("好きな食べ物", value=ex.get("food", ""), key=f"p_f_{i}")
            sh = st.text_input("シャンプー", value=ex.get("shampoo", ""), key=f"p_sh_{i}")
            yt = st.text_input("好きなYouTube", value=ex.get("youtube", ""), key=f"p_y_{i}")
            s = st.text_input("今の曲URL", value=ex.get("song_url", ""), key=f"p_s_{i}")
            ng = st.text_area("地雷", value=ex.get("ng", ""), key=f"p_ng_{i}")
            re = st.text_area("仲直り方法", value=ex.get("reconcile", ""), key=f"p_r_{i}")
            if st.button(f"{n}の情報を保存", key=f"p_b_{i}"):
                data["status"][k]["name"] = n
                data["profiles"][n] = {"birthday": bd, "job": jb, "hobby": hb, "mbti": m, "food": f, "shampoo": sh, "youtube": yt, "song_url": s, "ng": ng, "reconcile": re}
                save_data(data); st.rerun()

# --- その他のタブは継続 ---
with tabs[1]: st.markdown("<h1 style='text-align:center; color:#ff69b4; font-size:5rem;'>100%</h1>", unsafe_allow_html=True)
with tabs[3]:
    st.header("📸 アルバム")
    with st.expander("思い出を追加"):
        img_f = st.file_uploader("画像選択", type=["jpg", "png", "jpeg"])
        tit = st.text_input("タイトル", key="alb_tit")
        if st.button("保存", key="alb_save") and img_f:
            b64 = image_to_base64(Image.open(img_f))
            data["memories"].append({"date": str(date.today()), "title": tit, "img": b64})
            save_data(data); st.rerun()
    for m in reversed(data["memories"]):
        st.write(f"### {m['date']} {m['title']}")
        st.image(f"data:image/jpeg;base64,{m['img']}")
with tabs[4]: st.header("📅 予定")
with tabs[5]:
    st.header("🛡️ 設定")
    nd = st.date_input("出会った日", value=date.fromisoformat(data.get("first_meet", "2026-01-22")))
    if st.button("設定を更新"):
        data["first_meet"] = str(nd); save_data(data); st.rerun()