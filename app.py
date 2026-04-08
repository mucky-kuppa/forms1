import streamlit as st
import pandas as pd
from datetime import datetime
import csv
import io

# --- ページ設定 ---
st.set_page_config(page_title="展示会ヒアリング", page_icon="📝", layout="centered")

def reset_all_fields():
    # 質問ファイル以外をリセット
    keys_to_keep = ['uploaded_q_file']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.rerun()

# セッション初期化
if 'camera_on' not in st.session_state: st.session_state['camera_on'] = False
if 'saved_img' not in st.session_state: st.session_state['saved_img'] = None
if 'submitted_success' not in st.session_state: st.session_state['submitted_success'] = False

# --- サイドバー ---
st.sidebar.header("⚙️ システム設定")
uploaded_q_file = st.sidebar.file_uploader("1. questions.csv を選択", type=["csv"])

st.sidebar.divider()
if st.sidebar.button("🔄 次のお客様へ（入力をリセット）", type="secondary"):
    reset_all_fields()

# --- メインロジック ---
if uploaded_q_file:
    df_q = pd.read_csv(uploaded_q_file, encoding='utf_8_sig')

    if st.session_state['submitted_success']:
        st.balloons()
        st.success("✅ ヒアリング内容を確定しました！")
        
        # ファイル名に日時（秒まで）を付与して重複を回避
        now_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 指定のメッセージに変更
        st.info("続ける場合は、以下のボタンを押してください。")
        
        st.download_button(
            label="📥 CSVファイルを保存する",
            data=st.session_state['download_csv'],
            file_name=f"result_{now_str}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary" # 保存ボタンを強調
        )
        
        if st.button("⬅️ 次のお客様の入力を開始する"):
            reset_all_fields()
        st.stop()

    st.title("📝 展示会ヒアリング入力")

    # カメラセクション
    with st.expander("📸 名刺撮影", expanded=not st.session_state['saved_img']):
        if not st.session_state['camera_on']:
            if st.button("📷 カメラを起動する"):
                st.session_state['camera_on'] = True
                st.rerun()
        else:
            img_file = st.camera_input("撮影")
            if img_file:
                if st.button("✅ この画像を採用"):
                    st.session_state['saved_img'] = img_file
                    st.session_state['camera_on'] = False
                    st.rerun()

    st.divider()

    # フォームセクション
    st.header("📋 ヒアリング詳細")
    
    # ボタンを赤くするためのカスタムCSS（Streamlitの標準ボタンを赤色に変更）
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #ff4b4b;
            color: white;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.form("main_form", clear_on_submit=True):
        form_values = {}
        for _, row in df_q.iterrows():
            qid, qtype, qtext = str(row['question_id']), row['question_type'], row['question_text']
            opts = str(row['options']).split('|') if pd.notna(row['options']) else []

            if qtype == 'separator':
                st.divider()
                continue

            st.write(f"**{qtext}**")
            
            # 【横並び対応】
            if qtype == 'radio_grid' or qid == 'date':
                form_values[qid] = st.radio(qtext, opts, label_visibility="collapsed", horizontal=True, key=f"r_{qid}")
            
            elif qtype == 'checkbox_list':
                cols = st.columns(3)
                selected = []
                for i, opt in enumerate(opts):
                    with cols[i % 3]:
                        if st.checkbox(opt, key=f"cb_{qid}_{opt}"):
                            selected.append(opt)
                form_values[qid] = "|".join(selected)
                
            elif qtype == 'text':
                form_values[qid] = st.text_input(qtext, label_visibility="collapsed", key=f"t_{qid}")
            elif qtype == 'textarea':
                form_values[qid] = st.text_area(qtext, label_visibility="collapsed", key=f"a_{qid}")

        # 確定ボタン（CSSにより赤色になります）
        submit_clicked = st.form_submit_button("💾 データを確定", use_container_width=True)

        if submit_clicked:
            form_values['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            form_values['image_file'] = f"data/business_cards/card_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg" if st.session_state['saved_img'] else "No Image"
            
            # CSV化
            new_df = pd.DataFrame([form_values])
            output = io.StringIO()
            new_df.to_csv(output, index=False, encoding='utf_8_sig', quoting=csv.QUOTE_ALL)
            
            st.session_state['download_csv'] = output.getvalue()
            st.session_state['submitted_success'] = True
            st.rerun()
else:
    st.warning("サイドバーから questions.csv を指定してください。")
