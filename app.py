import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ==========================================
# 1. 質問データの読み込み
# ==========================================
def load_config():
    """
    サイドバーでアップロードされたCSV、またはSecretsからデータを読み込みます。
    """
    st.sidebar.title("⚙️ 設定")
    
    # サイドバーにファイルアップロードを配置
    uploaded_file = st.sidebar.file_uploader("質問CSVファイルをアップロード", type=['csv'])
    
    if uploaded_file is not None:
        # アップロードされたファイルを優先
        return pd.read_csv(uploaded_file)
    elif "questions_csv" in st.secrets:
        # Secretsに設定がある場合はそれを使用
        csv_raw = st.secrets["questions_csv"]
        return pd.read_csv(io.StringIO(csv_raw.strip()))
    else:
        st.warning("サイドバーからCSVをアップロードするか、Secretsを設定してください。")
        st.stop()

# ==========================================
# 2. メインアプリケーション
# ==========================================
def main():
    st.set_page_config(page_title="展示会ヒアリングシート", layout="wide")
    st.title("📝 展示会ヒアリング入力フォーム")

    # 質問データの取得（サイドバー経由）
    df_questions = load_config()
    
    # フォームの作成
    with st.form("hearing_form", clear_on_submit=True):
        
        entry_data = {}

        # ---------------------------------------------------------
        # レイヤー1：顧客基礎情報
        # ---------------------------------------------------------
        st.subheader("👤 顧客基礎情報")
        
        # 基礎情報に分類するIDの定義
        basic_info_ids = ['date', 'company', 'company2', 'department', 'title', 'name']
        
        # 2列レイアウト
        col1, col2 = st.columns(2)
        
        basic_df = df_questions[df_questions['question_id'].isin(basic_info_ids)]
        for i, (_, row) in enumerate(basic_df.iterrows()):
            q_id = row['question_id']
            q_type = row['question_type']
            q_text = row['question_text']
            options = str(row['options']).split('|') if pd.notna(row['options']) else []
            
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                if q_type == 'radio':
                    entry_data[q_id] = st.radio(q_text, options, key=f"basic_{q_id}")
                elif q_type == 'checkbox':
                    entry_data[q_id] = st.multiselect(q_text, options, key=f"basic_{q_id}")
                elif q_type == 'text':
                    entry_data[q_id] = st.text_input(q_text, key=f"basic_{q_id}")

        st.markdown("---")

        # ---------------------------------------------------------
        # レイヤー2：ヒアリング内容
        # ---------------------------------------------------------
        st.subheader("🔍 ヒアリング・案件詳細")
        
        # ヒアリング内容に分類するIDの定義
        hearing_info_ids = ['interest', 'opinion', 'kakezan', 'internal', 'internal_other']
        
        hearing_df = df_questions[df_questions['question_id'].isin(hearing_info_ids)]
        for _, row in hearing_df.iterrows():
            q_id = row['question_id']
            q_type = row['question_type']
            q_text = row['question_text']
            options = str(row['options']).split('|') if pd.notna(row['options']) else []

            if q_type == 'checkbox':
                entry_data[q_id] = st.multiselect(q_text, options, key=f"hear_{q_id}")
            elif q_type == 'textarea':
                entry_data[q_id] = st.text_area(q_text, key=f"hear_{q_id}")

        # ---------------------------------------------------------
        # 【コメントアウト】カメラ・画像保存機能
        # ---------------------------------------------------------
        # st.markdown("---")
        # st.subheader("📸 写真記録")
        # uploaded_img = st.file_uploader("名刺または展示物写真を撮影", type=['jpg', 'jpeg', 'png'])
        # if uploaded_img:
        #     st.image(uploaded_img, width=300)
        #     if st.button("この画像を採用"):
        #         st.info("画像保存ロジック（コメントアウト中）")
        
        st.markdown("---")
        
        # 送信ボタン
        submitted = st.form_submit_button("回答を送信して保存")
        
        if submitted:
            entry_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("✅ 送信が完了しました。")
            st.json(entry_data)

if __name__ == "__main__":
    main()
