import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt


def convert_to_int(value):
    if isinstance(value, str):
        match = re.search(r'\d+', value)
        if match:
            return int(match.group())
    return value


def map_ranks(df, columns, mapping):
    for column in columns:
        if column in df.columns:
            df[column] = df[column].map(mapping).infer_objects()
    return df


def process_dataframe(df):

    numeric_columns = [
        'Total years of experience in Façade Engineering?',
        'Total years of experience in UAE based Façade Industry?',
        'Design and Analysis - Overall Ranking',
        'Performance Analysis - Overall Ranking',
        'Technical Expertise - Overall Ranking',
        'Regulatory Compliance - Overall Ranking',
        'Collaborate and Communication - Overall Ranking',
        'Self-efficacy - Overall Ranking',
        'Adaptability - Overall Ranking',
        'Sustainability Awareness - Overall Ranking',
        'Ethics and Integrity - Overall Ranking',
        'Project Management - Overall Ranking'
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = df[column].apply(convert_to_int)

    rank_mapping = {
        'Rank 1': 1,
        'Rank 2': 2,
        'Rank 3': 3,
        'Rank 4': 4,
        'Rank 5': 5
    }

    sub_competency_columns = [
        col for col in df.columns if 'Sub-competencies Assessment' in col]

    df = map_ranks(df, sub_competency_columns, rank_mapping)

    relevance_mapping = {
        'D (Differentiator)': 0,
        'C (Core Activity)': 1
    }

    relevance_columns = [col for col in df.columns if 'Relevance Codes' in col]

    df = map_ranks(df, relevance_columns, relevance_mapping)

    return df


def calculate_weighted_means(df, columns):
    def calculate_weighted_value(row, column):
        value = row[column]
        if pd.notna(value):
            if isinstance(value, (int, float)):
                if value == 3:
                    return 1
                elif value == 2:
                    return 2
                elif value == 1:
                    return 3
        return 0

    weighted_means = {}
    for column in columns:
        weighted_sum = sum(calculate_weighted_value(row, column)
                           for _, row in df.iterrows() if pd.notna(row[column]))
        count = sum(1 for value in df[column] if pd.notna(value))
        weighted_means[column] = weighted_sum/count if count > 0 else 0

    return pd.Series(weighted_means)


def plot_competency_ranking(weighted_means, is_subcompetency=False):

    weighted_means_sorted = weighted_means.sort_values()

    fig_height = max(6, len(weighted_means_sorted) * 0.4)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    bars = ax.barh(
        y=range(len(weighted_means_sorted)),
        width=weighted_means_sorted.values,
        color='skyblue'
    )

    ax.set_yticks(range(len(weighted_means_sorted)))

    if is_subcompetency:
        labels = [label.replace('Sub-competencies Assessment [', '').replace(']', '')
                  for label in weighted_means_sorted.index]
    else:
        labels = [label.replace(' - Overall Ranking', '')
                  for label in weighted_means_sorted.index]

    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel('Weighted Mean')
    title = 'Weighted Means of Subcompetencies' if is_subcompetency else 'Weighted Means of Competencies'
    ax.set_title(title)

    # Add value labels on bars
    for i, v in enumerate(weighted_means_sorted.values):
        ax.text(v, i, f'{v:.2f}', va='center', fontsize=8)

    # Adjust layout
    plt.tight_layout()

    return fig


def get_competency_columns(df, competency):
    competency_mapping = {
        'Design and Analysis': [col for col in df.columns
                                if 'Sub-competencies Assessment' in col
                                and any(x in col for x in [
                                    'detailed drawing and specifications',
                                    'aesthetics and functional aspects',
                                    'Design Concept',
                                    'Fusion architecture',
                                    'façade materials',
                                    'installation detailing',
                                    'MTO for scope',
                                    'Preliminary Budgeting'
                                ])],

        'Performance Analysis': [col for col in df.columns
                                 if 'Sub-competencies Assessment' in col
                                 and any(x in col for x in [
                                     'energy within a design context',
                                     'performance criteria for energy efficiency',
                                     'façade technologies and materials',
                                     'Compliance with local codes',
                                     'Green building compliance'
                                 ])],

        'Technical Expertise': [col for col in df.columns
                                if 'Sub-competencies Assessment' in col
                                and any(x in col for x in [
                                    'Structural Analysis',
                                    'Building Systems Engineering',
                                    'Construction Technology',
                                    'structural engineering',
                                    'facade materials',
                                    'installation and maintenance',
                                    'Facade maintenance systems',
                                    'Seismic requirements'
                                ])],

        'Regulatory Compliance': [col for col in df.columns
                                  if 'Sub-competencies Assessment' in col
                                  and any(x in col for x in [
                                      'local and international building',
                                      'national and international regulations',
                                      'Compliance to local codes',
                                      'Green building compliance',
                                      'health and safety standards'
                                  ])],

        'Collaborate and Communication': [col for col in df.columns
                                          if 'Sub-competencies Assessment' in col
                                          and any(x in col for x in [
                                              'Communicate effectively',
                                              'collaborate and build consensus',
                                              'lead meetings',
                                              'design review meetings',
                                              'visual presentations'
                                          ])],

        'Self-efficacy': [col for col in df.columns
                          if 'Sub-competencies Assessment' in col
                          and any(x in col for x in [
                              'self-evaluate',
                             'Goal setting',
                             'Resilient'
                          ])],

        'Adaptability': [col for col in df.columns
                         if 'Sub-competencies Assessment' in col
                         and any(x in col for x in [
                             'Flexibility to respond',
                            'Adapt and improve'
                         ])],

        'Sustainability Awareness': [col for col in df.columns
                                     if 'Sub-competencies Assessment' in col
                                     and any(x in col for x in [
                                         'sustainable design',
                                         'energy efficiency',
                                         'sustainability implementation'
                                     ])],

        'Ethics and Integrity': [col for col in df.columns
                                 if 'Sub-competencies Assessment' in col
                                 and any(x in col for x in [
                                     'recognize ethical issues',
                                    'ethical perspectives'
                                 ])],

        'Project Management': [col for col in df.columns
                               if 'Sub-competencies Assessment' in col
                               and any(x in col for x in [
                                   'project schedules',
                                   'coordinate tasks',
                                   'costs and manage budgets',
                                   'Project Risk management'
                               ])]
    }
    return competency_mapping.get(competency, [])


def plot_competency_pie(df, competency):

    competency_columns = get_competency_columns(df, competency)

    if competency_columns:

        weighted_means = calculate_weighted_means(df, competency_columns)

        fig = plt.figure(figsize=(10, 6))
        plt.pie(
            weighted_means.values,
            labels=[label.split('[')[-1].split(']')[0]
                    for label in weighted_means.index],
            autopct='%1.1f%%',
            startangle=90
        )
        plt.title(f'{competency} Subcompetencies Distribution')

        return fig


def main():
    st.title("Facade Engineering Survey Analysis")

    uploaded_file = st.file_uploader(
        "Upload Survey Data", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:

            file_extension = uploaded_file.name.split('.')[-1]
            df = pd.read_csv(uploaded_file) if file_extension == 'csv' else pd.read_excel(
                uploaded_file)
            processed_df = process_dataframe(df)

            analysis_type = st.radio(
                "Select Analysis Type",
                ["Overall Competency", "Subcompetencies by Area"]
            )

            if analysis_type == "Overall Competency":

                overall_columns = [
                    'Design and Analysis - Overall Ranking',
                    'Performance Analysis - Overall Ranking',
                    'Technical Expertise - Overall Ranking',
                    'Regulatory Compliance - Overall Ranking',
                    'Collaborate and Communication - Overall Ranking',
                    'Self-efficacy - Overall Ranking',
                    'Adaptability - Overall Ranking',
                    'Sustainability Awareness - Overall Ranking',
                    'Ethics and Integrity - Overall Ranking',
                    'Project Management - Overall Ranking'
                ]

                weighted_means = calculate_weighted_means(
                    processed_df, overall_columns)

                fig = plt.figure(figsize=(10, 6))
                plt.pie(
                    weighted_means.values,
                    labels=[col.replace(' - Overall Ranking', '')
                            for col in weighted_means.index],
                    autopct='%1.1f%%',
                    startangle=90
                )
                plt.title('Overall Competency Distribution')
                st.pyplot(fig)

                st.write("### Overall Competency Rankings")
                st.dataframe(weighted_means.sort_values(ascending=False))

            else:

                selected_competency = st.selectbox(
                    "Select Competency for Analysis",
                    [
                        'Design and Analysis',
                        'Performance Analysis',
                        'Technical Expertise',
                        'Regulatory Compliance',
                        'Collaborate and Communication',
                        'Self-efficacy',
                        'Adaptability',
                        'Sustainability Awareness',
                        'Ethics and Integrity',
                        'Project Management'
                    ]
                )

                competency_columns = get_competency_columns(
                    processed_df, selected_competency)
                if competency_columns:
                    weighted_means = calculate_weighted_means(
                        processed_df, competency_columns)

                    fig = plt.figure(figsize=(10, 6))
                    plt.pie(
                        weighted_means.values,
                        labels=[label.split('[')[-1].split(']')[0]
                                for label in weighted_means.index],
                        autopct='%1.1f%%',
                        startangle=90
                    )
                    plt.title(
                        f'{selected_competency} Subcompetencies Distribution')
                    st.pyplot(fig)

                    st.write(f"### {selected_competency} Rankings")
                    st.dataframe(weighted_means.sort_values(ascending=False))

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


if __name__ == '__main__':
    main()