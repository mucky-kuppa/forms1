import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="集計ダッシュボード", layout="wide")

def load_data():
    if 'folder_path' not in st.session_state or not st.session_state['folder_path']:
        st.warning("メインページで作業フォルダを選択してください。")
        return None
    csv_path = os.path.join(st.session_state['folder_path'], "data", "results.csv")
    if not os.path.exists(csv_path):
        st.info("まだ保存されたデータがありません。")
        return None
    try:
        # 不正な行をスキップする設定(on_bad_lines)を追加
        return pd.read_csv(csv_path, encoding='utf_8_sig', on_bad_lines='warn')
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

def main():
    st.title("📊 ヒアリング集計")
    df = load_data()
    if df is None: return

    kpi1, kpi2 = st.columns(2)
    kpi1.metric("総件数", f"{len(df)} 件")
    kpi2.metric("最終更新", df['timestamp'].max() if 'timestamp' in df.columns else "-")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if 'company1' in df.columns:
            st.subheader("🏢 社名１分布")
            st.plotly_chart(px.pie(df, names='company1', hole=0.4), use_container_width=True)
    with c2:
        if 'date' in df.columns:
            st.subheader("📅 日別来場数")
            st.plotly_chart(px.bar(df['date'].value_counts().sort_index()), use_container_width=True)

    st.divider()
    st.subheader("🔧 課題・興味の集計")
    m1, m2 = st.columns(2)
    for col, ax in zip(['trouble', 'interest'], [m1, m2]):
        if col in df.columns:
            all_data = df[col].dropna().str.split('|').explode()
            fig = px.bar(all_data.value_counts(), orientation='h', title=f"項目別: {col}")
            ax.plotly_chart(fig, use_container_width=True)

    with st.expander("データ一覧"):
        st.dataframe(df)

if __name__ == "__main__":
    main()