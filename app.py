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
    # セッションを空にする（クラウドではフォルダパスの退避は不要）
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# セッション初期化
if 'camera_on' not in st.session_state: st.session_state['camera_on'] = False
if 'saved_img' not in st.session_state: st.session_state['saved_img'] = None
if 'submitted_success' not in st.session_state: st.session_state['submitted_success'] = False

# --- サイドバー ---
st.sidebar.header("⚙️ システム設定")
# 【変更点】クラウドでは作業フォルダを直接開けないため、質問ファイルをアップロードする形式に変更
uploaded_q_file = st.sidebar.file_uploader("questions.csv をアップロード", type="csv")

st.sidebar.divider()
if st.sidebar.button("🔄 全てを初期化して次の客へ", type="secondary"):
    reset_all_fields()

# --- メインロジック ---
if uploaded_q_file:
    # 質問データの読み込み
    df_q = pd.read_csv(uploaded_q_file, encoding='utf_8_sig')

    if st.session_state['submitted_success']:
        st.balloons()
        st.success("✅ 送信が完了しました！")
        st.info("※クラウド版ではブラウザ上で一時的に保持されます。")
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
            img_file = st.camera_input("撮影")
            if img_file:
                if st.button("✅ この画像を採用"):
                    # クラウドではファイルを直接保存せず、メモリ内に保持します
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
            qid, qtype, qtext = str(row['question_id']), row['question_type'], row['question_text']
            opts = str(row['options']).split('|') if pd.notna(row['options']) else []

            if qtype == 'separator':
                st.divider()
                continue

            st.write(f"**{qtext}**")
            if qtype == 'radio_grid' or qid == 'date':
                form_values[qid] = st.radio(qtext, opts, label_visibility="collapsed", horizontal=True, key=f"radio_{qid}")
            elif qtype == 'checkbox_list':
                cols = st.columns(3)
                selected = []
                for i, opt in enumerate(opts):
                    with cols[i % 3]:
                        if st.checkbox(opt, key=f"cb_{qid}_{opt}"):
                            selected.append(opt)
                form_values[qid] = "|".join(selected)
            elif qtype == 'text':
                form_values[qid] = st.text_input(qtext, label_visibility="collapsed", key=f"text_{qid}")
            elif qtype == 'textarea':
                form_values[qid] = st.text_area(qtext, label_visibility="collapsed", key=f"area_{qid}")

        if st.form_submit_button("💾 内容を確認（ダウンロード準備）", use_container_width=True):
            form_values['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 【重要】クラウドではサーバーのCドライブ等に保存できないため、CSVをメモリ上で作成します
            res_df = pd.DataFrame([form_values])
            csv_buffer = io.StringIO()
            res_df.to_csv(csv_buffer, index=False, encoding='utf_8_sig', quoting=csv.QUOTE_ALL)
            
            st.session_state['csv_data'] = csv_buffer.getvalue()
            st.session_state['submitted_success'] = True
            st.rerun()

    # 送信成功後のダウンロードボタン（クラウド環境での運用案）
    if st.session_state['submitted_success'] and 'csv_data' in st.session_state:
        st.download_button(
            label="📥 結果をCSVとして保存",
            data=st.session_state['csv_data'],
            file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
else:
    st.warning("左のサイドバーから questions.csv をアップロードしてください。")
