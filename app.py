import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px

# 1. ページ設定
st.set_page_config(page_title="App Dashboard", layout="wide")

def main():
    st.title("データ分析ダッシュボード")

    # 2. サイドバーでファイルアップロード
    st.sidebar.header("設定")
    uploaded_files = st.sidebar.file_uploader(
        "処理したいCSVファイルを選択してください", 
        type=["csv"], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} 個のファイルを読み込みました。")
        
        # 例：選択された最初のファイルをデータフレームにする
        for file in uploaded_files:
            st.subheader(f"ファイル内容の確認: {file.name}")
            
            # ファイルオブジェクトをそのままpandasに渡せます
            df = pd.read_csv(file)
            
            # データの表示
            st.dataframe(df.head())

            # 簡単な可視化（例：数値列があればグラフ化）
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if len(numeric_cols) >= 2:
                st.write("### 簡易グラフ")
                fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"{file.name} の散布図")
                st.plotly_chart(fig)
            else:
                st.info("数値データが不足しているため、グラフ表示をスキップします。")
                
            st.divider()
    else:
        st.info("左側のサイドバーからCSVファイルをアップロードしてください。")
        st.warning("※クラウド環境では PC のフォルダを直接参照（tkinter）できないため、このアップローダーを使用します。")

if __name__ == "__main__":
    main()
