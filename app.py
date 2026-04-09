import streamlit as st
import pandas as pd
import io
from datetime import datetime

# --- セキュリティ設定（SecretsからCSV読み込み） ---
def load_config():
    if "questions_csv" not in st.secrets:
        st.error("Secretsに 'questions_csv' が設定されていません。")
        st.stop()
    csv_raw = st.secrets["questions_csv"]
    return pd.read_csv(io.StringIO(csv_raw))

def main():
    st.set_page_config(page_title="展示会ヒアリングシート", layout="wide")
    st.title("📝 展示会ヒアリング入力")

    # 質問データの読み込み
    df_questions = load_config()
    
    # セッション状態で入力データを管理
    with st.form("survey_form", clear_on_submit=True):
        
        # ---------------------------------------------------------
        # レイヤー1：顧客基礎情報
        # ---------------------------------------------------------
        st.header("👤 顧客基礎情報")
        col1, col2 = st.columns(2)
        
        entry_data = {}
        
        # 基礎情報に分類するIDリスト
        basic_info_ids = ['date', 'company', 'company2', 'department', 'title', 'name']
        
        for _, row in df_questions.iterrows():
            q_id = row['question_id']
            if q_id in basic_info_ids:
                q_type = row['question_type']
                q_text = row['question_text']
                options = str(row['options']).split('|') if pd.notna(row['options']) else []

                # レイアウトを2列に分ける（適宜調整）
                target_col = col1 if basic_info_ids.index(q_id) % 2 == 0 else col2
                
                with target_col:
                    if q_type == 'radio':
                        entry_data[q_id] = st.radio(q_text, options, key=q_id)
                    elif q_type == 'checkbox':
                        entry_data[q_id] = st.multiselect(q_text, options, key=q_id)
                    elif q_type == 'text':
                        entry_data[q_id] = st.text_input(q_text, key=q_id)

        st.divider()

        # ---------------------------------------------------------
        # レイヤー2：ヒアリング内容
        # ---------------------------------------------------------
        st.header("🔍 ヒアリング内容")
        
        hearing_info_ids = ['interest', 'opinion', 'kakezan', 'internal', 'internal_other']
        
        for _, row in df_questions.iterrows():
            q_id = row['question_id']
            if q_id in hearing_info_ids:
                q_type = row['question_type']
                q_text = row['question_text']
                options = str(row['options']).split('|') if pd.notna(row['options']) else []

                if q_type == 'checkbox':
                    entry_data[q_id] = st.multiselect(q_text, options, key=q_id)
                elif q_type == 'textarea':
                    entry_data[q_id] = st.text_area(q_text, key=q_id)

        # ---------------------------------------------------------
        # 【コメントアウト】カメラ・画像保存機能
        # ---------------------------------------------------------
        # st.divider()
        # st.header("📸 写真記録")
        # uploaded_file = st.file_uploader("名刺または展示物写真を撮影", type=['jpg', 'jpeg', 'png'])
        # if uploaded_file:
        #     st.image(uploaded_file, width=300)
        #     if st.button("この画像を採用"):
        #         # upload_to_drive(uploaded_file, f"{entry_data.get('name')}_photo.jpg")
        #         st.info("画像保存ロジック（未有効）")
        
        st.divider()
        
        # 送信ボタン
        submitted = st.form_submit_button("回答を送信して保存")
        
        if submitted:
            entry_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("データを送信しました。")
            st.json(entry_data) # 確認用表示

if __name__ == "__main__":
    main()
