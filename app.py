import streamlit as st
import pandas as pd
import io
from datetime import datetime

# ==========================================
# 1. 質問データの読み込み（Secrets経由）
# ==========================================
def load_config():
    """
    Streamlit Cloudの管理画面 'Secrets' に保存されたCSVテキストを読み込みます。
    """
    if "questions_csv" not in st.secrets:
        st.error("⚠️ エラー: Secretsに 'questions_csv' が設定されていません。")
        st.info("Streamlitの管理画面で、CSV形式のテキストを questions_csv = '''...''' の形式で保存してください。")
        st.stop()
    
    csv_raw = st.secrets["questions_csv"]
    # 改行や空白のトリミングを行い、pandasで読み込む
    return pd.read_csv(io.StringIO(csv_raw.strip()))

# ==========================================
# 2. メインアプリケーション
# ==========================================
def main():
    st.set_page_config(page_title="展示会ヒアリングシート", layout="wide")
    st.title("📝 展示会ヒアリング入力フォーム")

    # 質問データの取得
    df_questions = load_config()
    
    # フォームの作成
    with st.form("hearing_form", clear_on_submit=True):
        
        entry_data = {}

        # ---------------------------------------------------------
        # レイヤー1：顧客基礎情報
        # ---------------------------------------------------------
        st.subheader("👤 顧客基礎情報")
        st.caption("名刺情報や来場日に関する項目")
        
        # 基礎情報に分類するIDの定義
        basic_info_ids = ['date', 'company', 'company2', 'department', 'title', 'name']
        
        # 2列レイアウトで表示
        col1, col2 = st.columns(2)
        
        # 基礎情報の描画ロジック
        basic_df = df_questions[df_questions['question_id'].isin(basic_info_ids)]
        for i, (_, row) in enumerate(basic_df.iterrows()):
            q_id = row['question_id']
            q_type = row['question_type']
            q_text = row['question_text']
            options = str(row['options']).split('|') if pd.notna(row['options']) else []
            
            # 左右交互に配置
            target_col = col1 if i % 2 == 0 else col2
            
            with target_col:
                if q_type == 'radio':
                    entry_data[q_id] = st.radio(q_text, options, key=q_id)
                elif q_type == 'checkbox':
                    entry_data[q_id] = st.multiselect(q_text, options, key=q_id)
                elif q_type == 'text':
                    entry_data[q_id] = st.text_input(q_text, key=q_id)

        st.markdown("---")

        # ---------------------------------------------------------
        # レイヤー2：ヒアリング内容
        # ---------------------------------------------------------
        st.subheader("🔍 ヒアリング・案件詳細")
        st.caption("ブースでの対話内容やアクションに関する項目")
        
        # ヒアリング内容に分類するIDの定義
        hearing_info_ids = ['interest', 'opinion', 'kakezan', 'internal', 'internal_other']
        
        # ヒアリング内容の描画ロジック
        hearing_df = df_questions[df_questions['question_id'].isin(hearing_info_ids)]
        for _, row in hearing_df.iterrows():
            q_id = row['question_id']
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
        # st.markdown("---")
        # st.subheader("📸 写真記録")
        # uploaded_file = st.file_uploader("名刺または展示物写真を撮影", type=['jpg', 'jpeg', 'png'])
        # if uploaded_file:
        #     st.image(uploaded_file, width=300)
        #     # 「採用」ボタンが押された時の処理
        #     if st.button("この画像を採用"):
        #         # upload_to_drive(uploaded_file, f"{entry_data.get('name', 'no_name')}.jpg")
        #         st.info("画像保存ロジックを実行しました（※現在はコメントアウト中）")
        
        st.markdown("---")
        
        # 送信ボタン
        submitted = st.form_submit_button("回答を送信して保存")
        
        if submitted:
            # 送信時の追加メタデータ
            entry_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 結果の表示
            st.success("✅ 送信が完了しました。")
            st.write("### 送信データ（プレビュー）")
            st.json(entry_data)
            
            # 実際の運用ではここでGoogleスプレッドシートやDBに保存する関数を呼び出します

if __name__ == "__main__":
    main()
