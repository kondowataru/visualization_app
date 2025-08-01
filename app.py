# app.py

import streamlit as st
import pandas as pd
# componentsから必要な関数をインポート
from components.graph_plotter import (
    plot_line_chart,
    plot_bar_chart,
    plot_stacked_bar_chart,
    plot_scatter_plot,
    plot_heatmap
)
from components.data_processor import (
    load_and_combine_csv,
    calculate_and_plot_average,
    aggregate_and_plot_time_series
)

st.set_page_config(layout="wide")

st.title('データ可視化Webアプリケーション')

st.write('CSVファイルをアップロードしてください。複数のファイルを選択することも可能です。')

# 複数のCSVファイルアップローダー
uploaded_files = st.file_uploader("CSVファイルを選択", type=["csv"], accept_multiple_files=True)

df = None # 初期化

if uploaded_files: # 少なくとも1つファイルがアップロードされた場合
    # data_processorモジュールから結合関数を呼び出す
    df = load_and_combine_csv(uploaded_files)

    if df is not None: # データフレームが正常に読み込まれた場合のみ処理を続行
        st.success(f'{len(uploaded_files)} 個のファイルをアップロードし、結合が完了しました！')

        st.subheader('結合されたデータのプレビュー（最初の5行）')
        st.dataframe(df.head())

        st.subheader('結合されたデータの基本情報')
        st.write(f'行数: {df.shape[0]}, 列数: {df.shape[1]}')
        st.write('データ型:')
        st.write(df.dtypes)

        # --- グラフ描画セクション ---
        st.subheader('グラフ描画セクション')
        st.write('---')

        graph_type = st.selectbox(
            '表示するグラフの種類を選択してください:',
            ('選択してください', '折れ線グラフ', '棒グラフ', '積み立てグラフ', '散布図', 'ヒートマップ')
        )

        if graph_type != '選択してください':
            st.write(f'**{graph_type} の設定**')

            columns = df.columns.tolist()

            if graph_type in ['折れ線グラフ', '棒グラフ', '積み立てグラフ']:
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_cols = st.multiselect('Y軸に使う列を1つ以上選択してください:', columns)

                if x_axis_col and y_axis_cols:
                    if graph_type == '折れ線グラフ':
                        plot_line_chart(df, x_axis_col, y_axis_cols)
                    elif graph_type == '棒グラフ':
                        plot_bar_chart(df, x_axis_col, y_axis_cols)
                    elif graph_type == '積み立てグラフ':
                        plot_stacked_bar_chart(df, x_axis_col, y_axis_cols)
                else:
                    st.warning("X軸とY軸の列を選択してください。")

            elif graph_type == '散布図':
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
                color_col = st.selectbox('色分けに使う列を選択してください (任意):', [''] + columns)

                if x_axis_col and y_axis_col:
                    plot_scatter_plot(df, x_axis_col, y_axis_col, color_col if color_col else None)
                else:
                    st.warning("X軸とY軸の列を選択してください。")

            elif graph_type == 'ヒートマップ':
                x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
                y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
                z_axis_col = st.selectbox('値を表すZ軸に使う列を選択してください (任意):', [''] + columns)

                if x_axis_col and y_axis_col:
                    plot_heatmap(df, x_axis_col, y_axis_col, z_axis_col if z_axis_col else None)
                else:
                    st.warning("X軸とY軸の列を選択してください。")

            else:
                st.info('グラフの種類を選択すると、設定オプションが表示されます。')

        # --- データ分析セクション ---
        st.subheader('データ分析')
        st.write('---')

        analysis_type = st.selectbox(
            '実行する分析を選択してください:',
            ('選択してください', '選択した列の平均値', '時系列データ集計と可視化')
        )

        if analysis_type == '選択した列の平均値':
            # data_processorモジュールから平均値計算関数を呼び出す
            calculate_and_plot_average(df)
        elif analysis_type == '時系列データ集計と可視化':
            # data_processorモジュールから時系列集計関数を呼び出す
            aggregate_and_plot_time_series(df)
        else:
            st.info('分析の種類を選択すると、オプションが表示されます。')

    else:
        st.warning("有効なCSVファイルが読み込まれませんでした。")

else:
    st.info('CSVファイルをアップロードしてお試しください。')