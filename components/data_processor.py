# components/data_processor.py

import pandas as pd
import streamlit as st # Streamlitのエラー表示に使うためインポート

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

                import plotly.express as px # 関数内でインポート
                st.subheader('平均値の棒グラフ')
                fig_avg_bar = px.bar(
                    average_values.reset_index(),
                    x='index',
                    y=0,
                    title='選択された列の平均値',
                    labels={'index': '列名', 0: '平均値'}
                )
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
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    value_col = st.selectbox('値を計算したい数値列を選択してください:', numeric_cols)

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
            import plotly.express as px # 関数内でインポート

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
                st.plotly_chart(fig, use_container_width=True)
                st.info("ヒートマップは、日ごとの時間帯別のパターンを視覚的に把握するのに適しています。")

            else:
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
                else:
                    fig = px.bar(
                        aggregated_df,
                        x='Period',
                        y='Average_Value',
                        title=plot_title,
                        labels={'Period': x_label, 'Average_Value': y_label}
                    )
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info('集計粒度を選択してください。')

    except KeyError as ke:
        st.error(f"選択した列が見つかりません: {ke}。列名を確認してください。")
    except Exception as e:
        st.error(f"分析中にエラーが発生しました: {e}")
        st.info("選択したタイムスタンプ列が正しい形式か、数値データ列が数値型か確認してください。")