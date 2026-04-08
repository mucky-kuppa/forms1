import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="App Dashboard", layout="wide")

st.title("📊 ヒアリングデータ集計ダッシュボード")

# サイドバーで対象ファイルを指定（これが「作業フォルダーの指定」の代わり）
st.sidebar.header("📁 データソース選択")
target_file = st.sidebar.file_uploader("集計対象の results.csv を選択", type="csv")

if target_file:
    df = pd.read_csv(target_file, encoding='utf_8_sig')
    
    st.sidebar.success(f"読み込み完了: {len(df)} 件のデータ")
    
    # メトリクス表示
    col1, col2, col3 = st.columns(3)
    col1.metric("総回答数", f"{len(df)} 件")
    col2.metric("最終更新", df['timestamp'].max() if 'timestamp' in df.columns else "-")
    
    st.divider()

    # データ一覧
    st.subheader("📋 回答詳細データ")
    st.dataframe(df, use_container_width=True)

    # 簡単な集計グラフ（例：回答日時の推移）
    if 'timestamp' in df.columns:
        st.subheader("📈 時系列推移")
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        date_counts = df['date'].value_counts().sort_index().reset_index()
        date_counts.columns = ['日付', '件数']
        fig = px.bar(date_counts, x='日付', y='件数', title="日別回答数")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("左側のサイドバーから結果ファイル（results.csv）を読み込んでください。")
