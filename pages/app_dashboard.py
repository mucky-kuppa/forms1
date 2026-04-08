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
    # クラウド版ではパス管理が不要なため、純粋にセッションをリセット
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# セッション初期化
if 'camera_on' not in st.session_state: st.session_state['camera_on'] = False
if 'saved_img' not in st.session_state: st.session_state['saved_img'] = None
if 'submitted_success' not in st.session_state: st.session_state['submitted_success'] = False

# --- サイドバー ---
st.sidebar.header("⚙️ システム設定")

# 【変更点】フォルダ指定の代わりに、質問ファイル(CSV)をアップロード
uploaded_q_file = st.sidebar.file_uploader(
    "1. questions.csv をアップロードしてください", 
    type=["csv"]
)

st.sidebar.divider()
if st.sidebar.button("🔄 全てを初期化して次の客へ", type="secondary"):
    reset_all_fields()

# --- メインロジック ---
if uploaded_q_file:
    # 質問データの読み込み 
    df_q = pd.read_csv(uploaded_q_file, encoding='utf_8_sig') [cite: 1]

    if st.session_state['submitted_success']:
        st.balloons()
        st.success("✅ 保存の準備が完了しました！")
        
        # 【重要】クラウドではサーバー保存ができないため、結果を自分のPCへダウンロードさせる
        if 'last_result_csv' in st.session_state:
            st.download_button(
                label="📥 ヒアリング結果をCSVで保存",
                data=st.session_state['last_result_csv'],
                file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        if st.button("⬅️ 次のお客様の入力を開始する", type="primary"):
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
            img_file = st.camera_input("撮影") [cite: 1]
            if img_file:
                if st.button("✅ この画像を採用"):
                    # クラウドではパス(saved_img_path)ではなく画像データそのものを保持
                    st.session_state['saved_img'] = img_file
                    st.session_state['camera_on'] = False
                    st.rerun()
            if st.button("❌ キャンセル"):
                st.session_state['camera_on'] = False
                st.rerun()

    if st.session_state['saved_img']:
        st.image(st.session_state['saved_img'], caption="撮影済み名刺", width=300)

    st.divider()

    # フォームセクション 
    st.header("📋 ヒアリング詳細")
    with st.form("main_form", clear_on_submit=True):
        form_values = {}
        for _, row in df_q.iterrows():
            qid, qtype, qtext = str(row['question_id']), row['question_type'], row['question_text'] [cite: 1]
            opts = str(row['options']).split('|') if pd.notna(row['options']) else [] [cite: 1]

            if qtype == 'separator':
                st.divider()
                continue

            st.write(f"**{qtext}**")
            if qtype == 'radio_grid' or qid == 'date':
                form_values[qid] = st.radio(qtext, opts, label_visibility="collapsed", horizontal=True, key=f"radio_{qid}") [cite: 1]
            elif qtype == 'checkbox_list':
                cols = st.columns(3)
                selected = []
                for i, opt in enumerate(opts):
                    with cols[i % 3]:
                        if st.checkbox(opt, key=f"cb_{qid}_{opt}"):
                            selected.append(opt)
                form_values[qid] = "|".join(selected) [cite: 1]
            elif qtype == 'text':
                form_values[qid] = st.text_input(qtext, label_visibility="collapsed", key=f"text_{qid}") [cite: 1]
            elif qtype == 'textarea':
                form_values[qid] = st.text_area(qtext, label_visibility="collapsed", key=f"area_{qid}") [cite: 1]

        if st.form_submit_button("💾 ヒアリング内容を確定", use_container_width=True):
            form_values['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") [cite: 1]
            form_values['image_status'] = "Captured" if st.session_state['saved_img'] else "No Image"
            
            # メモリ上にCSVを作成
            res_df = pd.DataFrame([form_values])
            output = io.StringIO()
            res_df.to_csv(output, index=False, encoding='utf_8_sig', quoting=csv.QUOTE_ALL)
            
            st.session_state['last_result_csv'] = output.getvalue()
            st.session_state['submitted_success'] = True
            st.rerun()
else:
    st.warning("左のサイドバーから questions.csv をアップロードしてください。")
