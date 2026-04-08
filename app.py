import streamlit as st
import pandas as pd
import os
#import tkinter as tk
#from tkinter import filedialog
from datetime import datetime
from PIL import Image
import csv

# --- ページ設定 ---
st.set_page_config(page_title="展示会ヒアリング", page_icon="📝", layout="centered")

# --- 初期化関数 (これが重要) ---
def reset_all_fields():
    # フォルダパスだけ退避してセッションを空にする
    current_path = st.session_state.get('folder_path', "")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state['folder_path'] = current_path
    st.rerun()

# --- フォルダ選択 ---
def select_folder():
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    folder_path = filedialog.askdirectory(master=root)
    root.destroy()
    return folder_path

# セッション初期化
if 'folder_path' not in st.session_state: st.session_state['folder_path'] = ""
if 'camera_on' not in st.session_state: st.session_state['camera_on'] = False
if 'saved_img_path' not in st.session_state: st.session_state['saved_img_path'] = None
if 'submitted_success' not in st.session_state: st.session_state['submitted_success'] = False

# --- サイドバー ---
st.sidebar.header("⚙️ システム設定")
if st.sidebar.button("📁 作業フォルダを選択"):
    path = select_folder()
    if path: st.session_state['folder_path'] = path

st.sidebar.divider()
if st.sidebar.button("🔄 全てを初期化して次の客へ", type="secondary"):
    reset_all_fields()

base_path = st.session_state['folder_path']
st.sidebar.text_input("現在のパス:", base_path, disabled=True)

# --- メインロジック ---
if base_path:
    data_dir = os.path.join(base_path, "data")
    img_dir = os.path.join(data_dir, "business_cards")
    csv_input_path = os.path.join(base_path, "questions.csv")
    os.makedirs(img_dir, exist_ok=True)

    if not os.path.exists(csv_input_path):
        st.error("questions.csv が見つかりません。")
        st.stop()
    
    df_q = pd.read_csv(csv_input_path, encoding='utf_8_sig')

    if st.session_state['submitted_success']:
        st.balloons()
        st.success("✅ 保存が完了しました！")
        if st.button("⬅️ 次のお客様の入力を開始する", type="primary"):
            reset_all_fields()
        st.stop()

    st.title("📝 展示会ヒアリング入力")

    # カメラセクション
    with st.expander("📸 名刺撮影", expanded=not st.session_state['saved_img_path']):
        if not st.session_state['camera_on']:
            if st.button("📷 カメラを起動する"):
                st.session_state['camera_on'] = True
                st.rerun()
        else:
            img_file = st.camera_input("撮影")
            if img_file:
                if st.button("✅ この画像を採用"):
                    img_filename = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    save_path = os.path.join(img_dir, img_filename)
                    Image.open(img_file).convert("RGB").save(save_path, quality=90)
                    st.session_state['saved_img_path'] = os.path.join("data", "business_cards", img_filename)
                    st.session_state['camera_on'] = False
                    st.rerun()
            if st.button("❌ キャンセル"):
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

        if st.form_submit_button("💾 ヒアリング内容を保存", use_container_width=True):
            form_values['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            form_values['image_file'] = st.session_state.get('saved_img_path', "No Image")
            
            result_csv_path = os.path.join(data_dir, "results.csv")
            # 列ズレ防止のため quoting=csv.QUOTE_ALL を使用
            res_df = pd.DataFrame([form_values])
            res_df.to_csv(result_csv_path, mode='a', header=not os.path.exists(result_csv_path), 
                          index=False, encoding='utf_8_sig', quoting=csv.QUOTE_ALL)
            st.session_state['submitted_success'] = True
            st.rerun()
else:
    st.warning("左のサイドバーから作業フォルダを選択してください。")
