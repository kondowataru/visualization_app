# components/graph_plotter.py

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Plotlyのカラーテーマリストの定義 ---
PLOTLY_TEMPLATES = [
    "plotly", "plotly_white", "plotly_dark", "gild", "ggplot2",
    "seaborn", "simple_white", "none"
]

# --- グラフ描画関数の変更 ---
# 各関数に title, x_label, y_label, color_theme 引数を追加

def plot_line_chart(df, x_col, y_cols, title=None, x_label=None, y_label=None, color_theme=None):
    """折れ線グラフを描画します。"""
    st.subheader('折れ線グラフ')
    if not isinstance(y_cols, list):
        y_cols = [y_cols]

    for y_col in y_cols:
        if y_col:
            # 軸ラベルを動的に設定
            labels = {x_col: x_label if x_label else x_col,
                      y_col: y_label if y_label else y_col}
            fig = px.line(df, x=x_col, y=y_col,
                          title=title if title else f'{y_col} vs {x_col} の折れ線グラフ',
                          labels=labels, template=color_theme)
            fig.update_layout(title_x=0.5) # ここを追加
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"折れ線グラフのY軸に有効な列が選択されていません。")


def plot_bar_chart(df, x_col, y_cols, title=None, x_label=None, y_label=None, color_theme=None):
    """棒グラフを描画します。"""
    st.subheader('棒グラフ')
    if not isinstance(y_cols, list):
        y_cols = [y_cols]

    for y_col in y_cols:
        if y_col:
            labels = {x_col: x_label if x_label else x_col,
                      y_col: y_label if y_label else y_col}
            fig = px.bar(df, x=x_col, y=y_col,
                         title=title if title else f'{y_col} vs {x_col} の棒グラフ',
                         labels=labels, template=color_theme)
            fig.update_layout(title_x=0.5) # ここを追加
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"棒グラフのY軸に有効な列が選択されていません。")

def plot_stacked_bar_chart(df, x_col, y_cols, title=None, x_label=None, y_label=None, color_theme=None):
    """積み立て棒グラフを描画します。"""
    st.subheader('積み立て棒グラフ')
    if not y_cols:
        st.warning("積み立てグラフには、少なくとも1つ以上のY軸の列が必要です。")
        return

    try:
        df_melted = df.melt(id_vars=[x_col], value_vars=y_cols, var_name="MetricType", value_name="Value")

        labels = {x_col: x_label if x_label else x_col,
                  "Value": y_label if y_label else "値"}
        fig = px.bar(df_melted, x=x_col, y="Value", color="MetricType",
                     title=title if title else f'{x_col}に対する積み立てグラフ',
                     barmode='stack', labels=labels, template=color_theme)
        fig.update_layout(title_x=0.5) # ここを追加
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"積み立てグラフの描画中にエラーが発生しました: {e}")
        st.info("選択した列が数値データであり、積み立てに適した形式か確認してください。")


def plot_scatter_plot(df, x_col, y_col, color_col=None, title=None, x_label=None, y_label=None, color_theme=None):
    """散布図を描画します。"""
    st.subheader('散布図')
    if x_col and y_col:
        labels = {x_col: x_label if x_label else x_col,
                  y_col: y_label if y_label else y_col}
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                         title=title if title else f'{y_col} vs {x_col} の散布図',
                         labels=labels, template=color_theme)
        fig.update_layout(title_x=0.5) # ここを追加
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("散布図のX軸とY軸に有効な列を選択してください。")

def plot_heatmap(df, x_col, y_col, z_col=None, title=None, x_label=None, y_label=None, color_theme=None):
    """ヒートマップを描画します。"""
    st.subheader('ヒートマップ')
    if x_col and y_col:
        if z_col:
            labels = {x_col: x_label if x_label else x_col,
                      y_col: y_label if y_label else y_col,
                      z_col: z_col}
            fig = px.density_heatmap(df, x=x_col, y=y_col, z=z_col,
                                     title=title if title else f'ヒートマップ ({z_col} by {x_col}, {y_col})',
                                     labels=labels, template=color_theme)
            fig.update_layout(title_x=0.5) # ここを追加
        else:
            st.info("ヒートマップには、通常X, Y軸に加え、色付けする値 (Z軸) が必要です。Z軸が選択されていないため、数値列の相関ヒートマップを表示します。")
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                corr = numeric_df.corr()
                fig = px.imshow(corr, text_auto=True, aspect="auto",
                                 title=title if title else "数値列の相関ヒートマップ",
                                 template=color_theme)
                fig.update_layout(title_x=0.5) # ここを追加
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("ヒートマップを描画するための数値列が見つかりません。")
                return

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ヒートマップのX軸とY軸に有効な列を選択してください。")