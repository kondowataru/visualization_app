# app.py

import streamlit as st
import pandas as pd
import numpy as np # 直接入力の初期データ生成に使うため残す
from datetime import datetime, timedelta # 直接入力の初期データ生成に使うため残す

# componentsから必要な関数をインポート
from components.graph_plotter import (
    plot_line_chart,
    plot_bar_chart,
    plot_stacked_bar_chart,
    plot_scatter_plot,
    plot_heatmap,
    PLOTLY_TEMPLATES
)
from components.data_processor import (
    load_and_combine_csv,
    calculate_and_plot_average,
    aggregate_and_plot_time_series,
    perform_advanced_statistics
)

st.set_page_config(layout="wide")

st.title('データ可視化Webアプリケーション')

# --- データ入力・編集セクション ---
st.header('1. データの入力・編集')
st.write('CSVファイルをアップロードするか、以下のテーブルで直接データを入力・編集してください。')

# 初期データフレームの生成（空のDFだと分かりにくいので、初期サンプルデータを入れておく）
if 'edited_df' not in st.session_state:
    # ユーザーが編集できる初期サンプルデータを作成
    sample_data_for_editor = {
        'Date': [datetime.now() - timedelta(days=i) for i in range(5)][::-1],
        'Product_A_Sales': [100, 105, 110, 95, 120],
        'Product_B_Sales': [50, 52, 55, 48, 60],
        'Customer_Rating': [4.5, 4.6, 4.7, 4.4, 4.8],
        'Region': ['East', 'West', 'East', 'Central', 'West']
    }
    st.session_state.edited_df = pd.DataFrame(sample_data_for_editor)
    # 日付列を日付型に変換しておく
    st.session_state.edited_df['Date'] = pd.to_datetime(st.session_state.edited_df['Date']).dt.date

# データエディタの表示
edited_df_from_editor = st.data_editor(
    st.session_state.edited_df,
    num_rows="dynamic", # 行の追加・削除を許可
    use_container_width=True,
    key="data_editor" # keyを指定
)

# エディタで編集されたデータをセッションステートに保存
st.session_state.edited_df = edited_df_from_editor

st.markdown('---') # 区切り線

# --- CSVファイルアップロードセクション（入力データがあればそちらを優先） ---
st.header('2. CSVファイルをアップロード (入力データがない場合のみ)')
st.write('直接入力されたデータがある場合、そちらが優先されます。')

uploaded_files = st.file_uploader("CSVファイルを選択", type=["csv"], accept_multiple_files=True)

df = None # 初期化

# データエディタに入力されたデータがあるか確認し、あればそれを優先
if not st.session_state.edited_df.empty:
    df = st.session_state.edited_df.copy()
    st.info('データエディタで入力されたデータを使用します。')
elif uploaded_files: # データエディタが空で、ファイルがアップロードされた場合
    df = load_and_combine_csv(uploaded_files)
    st.info(f'{len(uploaded_files)} 個のファイルをアップロードし、結合が完了しました！')
else: # どちらもデータがない場合
    st.info('データを直接入力するか、CSVファイルをアップロードしてください。')


if df is not None and not df.empty: # データフレームが正常に読み込まれた場合のみ処理を続行
    # データフレームの型を調整（data_editorからの入力はobject型になりがちなので）
    for col in df.columns:
        # 日付型に変換を試みる
        if 'Date' in col:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
            except:
                pass # 変換できなければそのまま

        # 数値型に変換を試みる
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        except:
            pass # 変換できなければそのまま

    st.subheader('現在のデータのプレビュー（最初の5行）')
    st.dataframe(df.head())

    st.subheader('現在のデータの基本情報')
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

        # --- グラフカスタマイズオプションの追加 ---
        st.sidebar.subheader('グラフカスタマイズオプション')
        custom_title = st.sidebar.text_input('グラフタイトル (任意):', '')
        custom_x_label = st.sidebar.text_input('X軸ラベル (任意):', '')
        custom_y_label = st.sidebar.text_input('Y軸ラベル (任意):', '')

        selected_color_theme = st.sidebar.selectbox(
            'カラーテーマを選択:',
            PLOTLY_TEMPLATES,
            index=PLOTLY_TEMPLATES.index("plotly") # デフォルトは'plotly'
        )
        # --- グラフカスタマイズオプションの追加ここまで ---

        if graph_type in ['折れ線グラフ', '棒グラフ', '積み立てグラフ']:
            x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
            y_axis_cols = st.multiselect('Y軸に使う列を1つ以上選択してください:', columns)

            if x_axis_col and y_axis_cols:
                plot_line_chart(df, x_axis_col, y_axis_cols,
                                title=custom_title, x_label=custom_x_label,
                                y_label=custom_y_label, color_theme=selected_color_theme)
            else:
                st.warning("X軸とY軸の列を選択してください。")

        elif graph_type == '散布図':
            x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
            y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
            color_col = st.selectbox('色分けに使う列を選択してください (任意):', [''] + columns)

            if x_axis_col and y_axis_col:
                plot_scatter_plot(df, x_axis_col, y_axis_col, color_col if color_col else None,
                                  title=custom_title, x_label=custom_x_label,
                                  y_label=custom_y_label, color_theme=selected_color_theme)
            else:
                st.warning("X軸とY軸の列を選択してください。")

        elif graph_type == 'ヒートマップ':
            x_axis_col = st.selectbox('X軸に使う列を選択してください:', columns, index=0)
            y_axis_col = st.selectbox('Y軸に使う列を選択してください:', columns)
            z_axis_col = st.selectbox('値を表すZ軸に使う列を選択してください (任意):', [''] + columns)

            if x_axis_col and y_axis_col:
                plot_heatmap(df, x_axis_col, y_axis_col, z_axis_col if z_axis_col else None,
                             title=custom_title, x_label=custom_x_label,
                             y_label=custom_y_label, color_theme=selected_color_theme)
            else:
                st.warning("X軸とY軸の列を選択してください。")

    else: # graph_type が '選択してください' の場合
        st.info('グラフの種類を選択すると、設定オプションが表示されます。')

    # --- データ分析セクション ---
    st.subheader('データ分析')
    st.write('---')

    analysis_type = st.selectbox(
        '実行する分析を選択してください:',
        ('選択してください', '選択した列の平均値', '時系列データ集計と可視化', '高度な統計分析')
    )

    if analysis_type == '選択した列の平均値':
        calculate_and_plot_average(df)
    elif analysis_type == '時系列データ集計と可視化':
        aggregate_and_plot_time_series(df)
    elif analysis_type == '高度な統計分析':
        perform_advanced_statistics(df)
    else:
        st.info('分析の種類を選択すると、オプションが表示されます。')

else: # データフレームがNoneまたは空の場合
    pass # 上の st.info() でメッセージは表示済み