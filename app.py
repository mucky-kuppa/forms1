import streamlit as st
import pandas as pd
from datetime import datetime
import csv
import io

# --- ページ設定 ---
st.set_page_config(page_title="展示会ヒアリング", page_icon="📝", layout="centered")

def reset_all_fields():
    # 蓄積用データと質問ファイル以外をリセット
    keys_to_keep = ['existing_data', 'uploaded_q_file']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.rerun()

# セッション初期化
if 'existing_data' not in st.session_state: st.session_state['existing_data'] = None
if 'camera_on' not in st.session_state: st.session_state['camera_on'] = False
if 'saved_img' not in st.session_state: st.session_state['saved_img'] = None
if 'submitted_success' not in st.session_state: st.session_state['submitted_success'] = False

# --- サイドバー ---
st.sidebar.header("⚙️ システム・フォルダ設定")

# 1. 質問ファイルの読み込み
uploaded_q_file = st.sidebar.file_uploader("questions.csv を選択", type=["csv"])

# 2. 蓄積データの読み込み（これまでの results.csv を入れることで継続蓄積が可能）
uploaded_res_file = st.sidebar.file_uploader("これまでの results.csv を選択（追記用）", type=["csv"])
if uploaded_res_file:
    st.session_state['existing_data'] = pd.read_csv(uploaded_res_file, encoding='utf_8_sig')

st.sidebar.divider()
if st.sidebar.button("🔄 次のお客様へ（リセット）", type="secondary"):
    reset_all_fields()

# --- メインロジック ---
if uploaded_q_file:
    df_q = pd.read_csv(uploaded_q_file, encoding='utf_8_sig')

    if st.session_state['submitted_success']:
        st.balloons()
        st.success("✅ ヒアリング内容を確定しました！")
        
        # ダウンロードボタン（蓄積された全体データを出力）
        st.download_button(
            label="📥 更新された results.csv をダウンロードして保存",
            data=st.session_state['download_csv'],
            file_name="results.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.info("※ダウンロードしたファイルをPCの作業フォルダに上書きしてください。")
        
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
            
            # 【修正】選択肢を横に並べる (label_visibility="collapsed"で余白削減)
            if qtype == 'radio_grid' or qid == 'date':
                form_values[qid] = st.radio(qtext, opts, label_visibility="collapsed", horizontal=True, key=f"r_{qid}")
            
            elif qtype == 'checkbox_list':
                # チェックボックスを3列に並べる
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

        if st.form_submit_button("💾 内容を保存してダウンロード準備", use_container_width=True):
            form_values['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 新規データ
            new_df = pd.DataFrame([form_values])
            
            # 【蓄積ロジック】既存データがあれば結合する
            if st.session_state['existing_data'] is not None:
                final_df = pd.concat([st.session_state['existing_data'], new_df], ignore_index=True)
            else:
                final_df = new_df
            
            # ダウンロード用バッファ
            output = io.StringIO()
            final_df.to_csv(output, index=False, encoding='utf_8_sig', quoting=csv.QUOTE_ALL)
            st.session_state['download_csv'] = output.getvalue()
            
            # 次の入力のためにセッションを更新
            st.session_state['existing_data'] = final_df
            st.session_state['submitted_success'] = True
            st.rerun()
else:
    st.warning("サイドバーから questions.csv を指定してください。")
