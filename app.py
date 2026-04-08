import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image
import csv
import io

# --- ページ設定 ---
st.set_page_config(page_title="展示会ヒアリング", page_icon="📝", layout="centered")

# --- 初期化関数 ---
def reset_all_fields():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# セッション初期化
if 'camera_on' not in st.session_state: st.session_state['camera_on'] = False
if 'saved_img' not in st.session_state: st.session_state['saved_img'] = None
if 'submitted_success' not in st.session_state: st.session_state['submitted_success'] = False

# --- サイドバー ---
st.sidebar.header("⚙️ システム設定")

# 【変更点】フォルダー選択の代わりに「起点となるCSV」を指定
uploaded_q_file = st.sidebar.file_uploader(
    "作業の起点となる questions.csv を選択してください", 
    type=["csv"]
)

if uploaded_q_file:
    # 仮想的な「作業フォルダー」の名前として保持
    st.session_state['working_folder'] = "Current Project"
    st.sidebar.success(f"作業対象: {uploaded_q_file.name}")

st.sidebar.divider()
if st.sidebar.button("🔄 全てを初期化して次の客へ", type="secondary"):
    reset_all_fields()

# --- メインロジック ---
if uploaded_q_file:
    # 質問データの読み込み
    df_q = pd.read_csv(uploaded_q_file, encoding='utf_8_sig')

    if st.session_state['submitted_success']:
        st.balloons()
        st.success("✅ ヒアリング完了！データを一時保存しました。")
        
        # クラウド版では最後にまとめてDLするか、API等で送る設計が一般的です
        if 'last_result_csv' in st.session_state:
            st.download_button(
                label="📥 この内容を results.csv としてダウンロード",
                data=st.session_state['last_result_csv'],
                file_name="results.csv",
                mime="text/csv"
            )

        if st.button("⬅️ 次のお客様の入力を開始する", type="primary"):
            reset_all_fields()
        st.stop()

    st.title("📝 展示会ヒアリング入力")

    # カメラセクション (名刺撮影)
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
    with st.form("main_form", clear_on_submit=True):
        form_values = {}
        for _, row in df_q.iterrows():
            qid, qtype, qtext = str(row['question_id']), row['question_type'], row['question_text']
            opts = str(row['options']).split('|') if pd.notna(row['options']) else []

            if qtype == 'separator':
                st.divider()
                continue

            st.write(f"**{qtext}**")
            if qtype == 'radio_grid' or qid == 'date':
                form_values[qid] = st.radio(qtext, opts, horizontal=True, key=f"radio_{qid}")
            elif qtype == 'checkbox_list':
                selected = [opt for opt in opts if st.checkbox(opt, key=f"cb_{qid}_{opt}")]
                form_values[qid] = "|".join(selected)
            elif qtype in ['text', 'textarea']:
                func = st.text_input if qtype == 'text' else st.text_area
                form_values[qid] = func(qtext, key=f"input_{qid}")

        if st.form_submit_button("💾 データを確定する", use_container_width=True):
            form_values['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 内部的な「フォルダー構成」をシミュレートしたパスを記録
            form_values['image_path'] = f"data/business_cards/card_{datetime.now().strftime('%m%d%H%M')}.jpg"
            
            # CSV作成
            res_df = pd.DataFrame([form_values])
            output = io.StringIO()
            res_df.to_csv(output, index=False, encoding='utf_8_sig', quoting=csv.QUOTE_ALL)
            
            st.session_state['last_result_csv'] = output.getvalue()
            st.session_state['submitted_success'] = True
            st.rerun()
else:
    st.warning("左のサイドバーから questions.csv を指定してください。")
