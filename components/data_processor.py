# components/data_processor.py

import pandas as pd
import streamlit as st # Streamlitのエラー表示に使うためインポート
import plotly.express as px # 新しくインポート。ヒートマップ用

def load_and_combine_csv(uploaded_files):
    """
    複数のCSVファイルを読み込み、結合してDataFrameを返します。
    エラーが発生した場合はNoneを返します。
    """
    if not uploaded_files:
        return None

    combined_df_list = []
    for file in uploaded_files:
        try:
            df_single = pd.read_csv(file)
            combined_df_list.append(df_single)
        except Exception as e:
            st.error(f"ファイル '{file.name}' の読み込み中にエラーが発生しました: {e}")
            st.info("CSVファイルの形式が正しいか、またエンコーディングがUTF-8であるか確認してください。")
            continue

    if combined_df_list:
        try:
            df = pd.concat(combined_df_list, ignore_index=True)
            return df
        except Exception as e:
            st.error(f"結合されたデータの処理中にエラーが発生しました: {e}")
            st.info("結合しようとしているCSVファイルの列名や構造が大きく異なる場合、結合に失敗する可能性があります。")
            return None
    return None

def calculate_and_plot_average(df):
    """
    データフレームから選択された数値列の平均値を計算し、表と棒グラフで表示します。
    """
    st.write('選択した数値列の平均値を計算し、プロットします。')

    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

    if not numeric_columns:
        st.warning("データフレームに数値型の列が見つかりません。")
        return

    cols_to_average = st.multiselect(
        '平均値を計算したい数値列を選択してください:',
        numeric_columns
    )

    if st.button('平均値を計算しプロット'):
        if cols_to_average:
            try:
                average_values = df[cols_to_average].mean()

                st.subheader('計算結果（平均値）')
                st.dataframe(average_values.reset_index().rename(columns={'index': '列名', 0: '平均値'}))

                # plotly.express はファイルの先頭でインポート済
                st.subheader('平均値の棒グラフ')
                fig_avg_bar = px.bar(
                    average_values.reset_index(),
                    x='index',
                    y=0,
                    title='選択された列の平均値',
                    labels={'index': '列名', 0: '平均値'}
                )
                fig_avg_bar.update_layout(title_x=0.5) # タイトル中央寄せ
                st.plotly_chart(fig_avg_bar, use_container_width=True)

            except Exception as e:
                st.error(f"平均値の計算またはプロット中にエラーが発生しました: {e}")
                st.info("選択した列がすべて数値データであるか確認してください。")
        else:
            st.warning("平均値を計算したい列を1つ以上選択してください。")

def aggregate_and_plot_time_series(df):
    """
    時系列データを指定された粒度で集計し、表とグラフで表示します。
    """
    st.write('タイムスタンプ列と数値列を選択し、集計粒度を指定してプロットします。')

    columns = df.columns.tolist()

    time_col = st.selectbox('タイムスタンプ列を選択してください:', columns)
    numeric_columns = df.select_dtypes(include=['number']).columns.tolist() # Numeric columns here
    value_col = st.selectbox('値を計算したい数値列を選択してください:', numeric_columns)

    if not time_col or not value_col:
        st.warning("タイムスタンプ列と数値データ列を選択してください。")
        return

    try:
        df_copy = df.copy() # 元のDataFrameを変更しないようにコピー
        df_copy[time_col] = pd.to_datetime(df_copy[time_col])

        aggregation_granularity = st.selectbox(
            '集計粒度を選択してください:',
            (
                '選択してください',
                '日ごとの時間帯別平均',
                '時間帯別平均 (全期間)',
                '日別平均',
                '曜日別平均',
                '月別平均',
                '年別平均'
            )
        )

        if aggregation_granularity != '選択してください':
            st.write(f'**{aggregation_granularity} の集計結果**')
            aggregated_df = None
            plot_title = ""
            x_label = ""
            y_label = f'{value_col}の平均'
            # plotly.express はファイルの先頭でインポート済

            if aggregation_granularity == '日ごとの時間帯別平均':
                df_copy['hour'] = df_copy[time_col].dt.hour
                df_copy['date'] = df_copy[time_col].dt.date
                aggregated_df = df_copy.pivot_table(
                    values=value_col,
                    index='hour',
                    columns='date',
                    aggfunc='mean'
                )
                st.subheader('集計結果（表）')
                st.dataframe(aggregated_df)

                df_plot_heatmap = aggregated_df.reset_index().melt(
                    id_vars='hour',
                    var_name='Date',
                    value_name='Average_Value'
                )
                fig = px.density_heatmap(
                    df_plot_heatmap,
                    x='Date',
                    y='hour',
                    z='Average_Value',
                    title=f'日ごとの時間帯別平均 {value_col}',
                    labels={'hour': '時間帯 (h)', 'Date': '日付', 'Average_Value': y_label}
                )
                fig.update_layout(title_x=0.5) # タイトル中央寄せ
                st.plotly_chart(fig, use_container_width=True)
                st.info("ヒートマップは、日ごとの時間帯別のパターンを視覚的に把握するのに適しています。")

            else: # その他の粒度
                if aggregation_granularity == '時間帯別平均 (全期間)':
                    df_copy['period'] = df_copy[time_col].dt.hour
                    plot_title = f'全期間における時間帯別平均 {value_col}'
                    x_label = '時間帯 (h)'
                elif aggregation_granularity == '日別平均':
                    df_copy['period'] = df_copy[time_col].dt.date
                    plot_title = f'日別平均 {value_col}'
                    x_label = '日付'
                elif aggregation_granularity == '曜日別平均':
                    df_copy['period'] = df_copy[time_col].dt.day_name()
                    categories = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    df_copy['period'] = pd.Categorical(df_copy['period'], categories=categories, ordered=True)
                    plot_title = f'曜日別平均 {value_col}'
                    x_label = '曜日'
                elif aggregation_granularity == '月別平均':
                    df_copy['period'] = df_copy[time_col].dt.to_period('M').astype(str)
                    plot_title = f'月別平均 {value_col}'
                    x_label = '月'
                elif aggregation_granularity == '年別平均':
                    df_copy['period'] = df_copy[time_col].dt.year
                    plot_title = f'年別平均 {value_col}'
                    x_label = '年'

                aggregated_df = df_copy.groupby('period')[value_col].mean().reset_index()
                aggregated_df.columns = ['Period', 'Average_Value']

                st.subheader('集計結果（表）')
                st.dataframe(aggregated_df)

                if aggregation_granularity in ['日別平均', '月別平均', '年別平均', '時間帯別平均 (全期間)']:
                    fig = px.line(
                        aggregated_df,
                        x='Period',
                        y='Average_Value',
                        title=plot_title,
                        labels={'Period': x_label, 'Average_Value': y_label}
                    )
                else: # 曜日別平均などは棒グラフの方が自然
                    fig = px.bar(
                        aggregated_df,
                        x='Period',
                        y='Average_Value',
                        title=plot_title,
                        labels={'Period': x_label, 'Average_Value': y_label}
                    )
                fig.update_layout(title_x=0.5) # タイトル中央寄せ
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info('集計粒度を選択してください。')

    except KeyError as ke:
        st.error(f"選択した列が見つかりません: {ke}。列名を確認してください。")
    except Exception as e:
        st.error(f"分析中にエラーが発生しました: {e}")
        st.info("選択したタイムスタンプ列が正しい形式か、数値データ列が数値型か確認してください。")

def perform_advanced_statistics(df):
    """
    データフレームに対して高度な統計分析（記述統計量、相関行列）を実行し、表示します。
    """
    st.write('選択した数値列の基本的な統計量と相関行列を計算し表示します。')

    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

    if not numeric_columns:
        st.warning("データフレームに数値型の列が見つかりません。統計分析を実行できません。")
        return

    st.subheader('1. 基本的な記述統計量')
    st.info("選択した数値列の合計、平均、標準偏差、最小値、最大値などを表示します。")

    cols_for_describe = st.multiselect(
        '統計量を表示したい数値列を選択してください:',
        numeric_columns,
        default=numeric_columns # デフォルトで全ての数値列を選択
    )

    if cols_for_describe:
        try:
            # df.describe()で記述統計量を計算
            descriptive_stats = df[cols_for_describe].describe()
            st.dataframe(descriptive_stats)
        except Exception as e:
            st.error(f"記述統計量の計算中にエラーが発生しました: {e}")
            st.info("選択した列がすべて数値データであることを確認してください。")
    else:
        st.warning("統計量を表示したい列を1つ以上選択してください。")

    st.subheader('2. 相関行列のヒートマップ')
    st.info("選択した複数の数値列間の相関関係をヒートマップで可視化します。値が1に近いほど強い正の相関、-1に近いほど強い負の相関があります。")

    cols_for_correlation = st.multiselect(
        '相関を計算したい数値列を2つ以上選択してください:',
        numeric_columns,
        default=numeric_columns if len(numeric_columns) >= 2 else [] # 数値列が2つ以上あればデフォルトで選択
    )

    if st.button('相関行列を計算しプロット'):
        if len(cols_for_correlation) >= 2:
            try:
                # 相関行列を計算
                correlation_matrix = df[cols_for_correlation].corr()

                st.subheader('相関行列（表）')
                st.dataframe(correlation_matrix)

                # 相関行列をヒートマップで可視化
                fig_corr_heatmap = px.imshow(
                    correlation_matrix,
                    text_auto=True, # セルに値を自動表示
                    aspect="auto", # アスペクト比を自動調整
                    title='選択された列間の相関行列',
                    color_continuous_scale=px.colors.sequential.Viridis # カラーバーのスケール
                )
                fig_corr_heatmap.update_layout(title_x=0.5) # タイトル中央寄せ
                st.plotly_chart(fig_corr_heatmap, use_container_width=True)

            except Exception as e:
                st.error(f"相関行列の計算またはプロット中にエラーが発生しました: {e}")
                st.info("選択した列がすべて数値データであり、計算可能な状態であることを確認してください。")
        else:
            st.warning("相関を計算するには、2つ以上の数値列を選択してください。")