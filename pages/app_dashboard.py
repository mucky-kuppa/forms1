import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="App Dashboard", layout="wide")
st.title("📊 複数データ一括集計ダッシュボード")

st.sidebar.header("📁 データ読み込み")
uploaded_files = st.sidebar.file_uploader(
    "溜まった結果CSV(result_*.csv)をすべて選択してください", 
    type=["csv"], 
    accept_multiple_files=True
)

if uploaded_files:
    df_list = [pd.read_csv(f, encoding='utf_8_sig') for f in uploaded_files]
    df = pd.concat(df_list, ignore_index=True)
    
    st.sidebar.success(f"{len(uploaded_files)} 個のファイルを結合しました。")
    st.subheader("📋 統合データプレビュー")
    st.dataframe(df, use_container_width=True)

    if 'timestamp' in df.columns:
        st.subheader("📈 日別回答トレンド")
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        date_counts = df['date'].value_counts().reset_index().sort_values('index')
        date_counts.columns = ['日付', '件数']
        fig = px.bar(date_counts, x='日付', y='件数')
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("サイドバーから結果CSVを選択してください。")
