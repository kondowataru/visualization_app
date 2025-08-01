# components/graph_plotter.py

import streamlit as st

def plot_line_chart(df, x_col, y_cols):
    """折れ線グラフを描画します。"""
    import plotly.express as px # 関数内でインポート
    st.subheader('折れ線グラフ')
    if not isinstance(y_cols, list):
        y_cols = [y_cols]

    for y_col in y_cols:
        if y_col:
            fig = px.line(df, x=x_col, y=y_col,
                          title=f'{y_col} vs {x_col} の折れ線グラフ')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"折れ線グラフのY軸に有効な列が選択されていません。")


def plot_bar_chart(df, x_col, y_cols):
    """棒グラフを描画します。"""
    import plotly.express as px # 関数内でインポート
    st.subheader('棒グラフ')
    if not isinstance(y_cols, list):
        y_cols = [y_cols]

    for y_col in y_cols:
        if y_col:
            fig = px.bar(df, x=x_col, y=y_col,
                         title=f'{y_col} vs {x_col} の棒グラフ')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"棒グラフのY軸に有効な列が選択されていません。")

def plot_stacked_bar_chart(df, x_col, y_cols):
    """積み立て棒グラフを描画します。"""
    import plotly.express as px # 関数内でインポート
    import pandas as pd # meltのためにpandasは必要
    st.subheader('積み立て棒グラフ')
    if not y_cols:
        st.warning("積み立てグラフには、少なくとも1つ以上のY軸の列が必要です。")
        return

    try:
        df_melted = df.melt(id_vars=[x_col], value_vars=y_cols, var_name="MetricType", value_name="Value")

        fig = px.bar(df_melted, x=x_col, y="Value", color="MetricType",
                     title=f'{x_col}に対する積み立てグラフ',
                     barmode='stack')

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"積み立てグラフの描画中にエラーが発生しました: {e}")
        st.info("選択した列が数値データであり、積み立てに適した形式か確認してください。")


def plot_scatter_plot(df, x_col, y_col, color_col=None):
    """散布図を描画します。"""
    import plotly.express as px # 関数内でインポート
    st.subheader('散布図')
    if x_col and y_col:
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                         title=f'{y_col} vs {x_col} の散布図')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("散布図のX軸とY軸に有効な列を選択してください。")

def plot_heatmap(df, x_col, y_col, z_col=None):
    """ヒートマップを描画します。"""
    import plotly.express as px # 関数内でインポート
    import pandas as pd # select_dtypesのためにpandasは必要
    st.subheader('ヒートマップ')
    if x_col and y_col:
        if z_col:
            fig = px.density_heatmap(df, x=x_col, y=y_col, z=z_col,
                                     title=f'ヒートマップ ({z_col} by {x_col}, {y_col})')
        else:
            st.info("ヒートマップには、通常X, Y軸に加え、色付けする値 (Z軸) が必要です。Z軸が選択されていないため、数値列の相関ヒートマップを表示します。")
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                corr = numeric_df.corr()
                fig = px.imshow(corr, text_auto=True, aspect="auto",
                                 title="数値列の相関ヒートマップ")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("ヒートマップを描画するための数値列が見つかりません。")
                return

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ヒートマップのX軸とY軸に有効な列を選択してください。")