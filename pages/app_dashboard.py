import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="App Dashboard", layout="wide")
st.title("📊 複数データ一括集計ダッシュボード")

st.sidebar.header("📁 データ読み込み")
# 【修正】複数ファイルのアップロードを許可
uploaded_files = st.sidebar.file_uploader(
    "蓄積された result_*.csv ファイルをすべて選択してください", 
    type=["csv"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 全ファイルを読み込んでリストに格納
    df_list = []
    for file in uploaded_files:
        temp_df = pd.read_csv(file, encoding='utf_8_sig')
        df_list.append(temp_df)
    
    # データを結合
    df = pd.concat(df_list, ignore_index=True)
    
    st.sidebar.success(f"合計 {len(uploaded_files)} 個のファイルを結合しました。")
    st.sidebar.info(f"総データ件数: {len(df)} 件")

    # データ表示
    st.subheader("📋 結合済みデータ一覧")
    st.dataframe(df, use_container_width=True)

    # 日時データがある場合の時系列グラフ
    if 'timestamp' in df.columns:
        st.subheader("📈 日別回答数（集計）")
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        date_counts = df['date'].value_counts().reset_index()
        date_counts.columns = ['日付', '件数']
        date_counts = date_counts.sort_values('日付')
        
        fig = px.bar(date_counts, x='日付', y='件数', color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("サイドバーから1つ以上の結果CSVファイルをアップロードしてください。")
