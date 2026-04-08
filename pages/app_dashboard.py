import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="App Dashboard", layout="wide")
st.title("📊 集計ダッシュボード")

target_file = st.sidebar.file_uploader("蓄積された results.csv を選択", type="csv")

if target_file:
    df = pd.read_csv(target_file, encoding='utf_8_sig')
    st.success(f"データ読み込み完了: {len(df)} 件")
    
    # 横並び表示
    st.dataframe(df, use_container_width=True)
    
    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        fig = px.bar(df['date'].value_counts().reset_index(), x='index', y='date', title="日別回答数")
        st.plotly_chart(fig, use_container_width=True)
