import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

def extract_bracket_content(column_name):
    match = re.search(r'\[(.*?)\]', column_name)
    return match.group(1) if match else column_name

def calculate_weighted_average(series):
    series = pd.to_numeric(series, errors='coerce')
    count_1 = (series == 1).sum()
    count_2 = (series == 2).sum()
    count_3 = (series == 3).sum()
    weighted_sum = (count_1 * 3) + (count_2 * 2) + (count_3 * 1)
    return weighted_sum / (count_1 + count_2 + count_3) if (count_1 + count_2 + count_3) > 0 else 0

def calculate_competency_averages(df, competencies):
    averages = {}
    for comp_name, comp_col in competencies.items():
        avg = calculate_weighted_average(df[comp_col])
        averages[comp_name] = avg
    return averages

def get_subcompetencies(df, competency_name):
    subcols = [col for col in df.columns if competency_name in col and '[' in col 
               and not col.startswith('Relevance')]
    return {col: extract_bracket_content(col) for col in subcols}

def get_relevance_codes(df, competency_name):
    relcols = [col for col in df.columns if competency_name in col 
               and col.startswith('Relevance')]
    return {col: extract_bracket_content(col) for col in relcols}

def main():
    st.title("Facade Engineering Competency Analysis")
    
    uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
    
    if uploaded_file is None:
        st.info("Please upload a CSV file to begin analysis")
        return
    
    try:
        df = pd.read_csv(uploaded_file)
        competencies = {
            'Design and Analysis': 'Design and Analysis - Overall Ranking',
            'Performance Analysis': 'Performance Analysis - Overall Ranking',
            'Technical Expertise': 'Technical Expertise - Overall Ranking',
            'Regulatory Compliance': 'Regulatory Compliance - Overall Ranking',
            'Collaborate and Communication': 'Collaborate and Communication - Overall Ranking',
            'Self-efficacy': 'Self-efficacy - Overall Ranking',
            'Adaptability': 'Adaptability - Overall Ranking',
            'Sustainability Awareness': 'Sustainability Awareness - Overall Ranking',
            'Ethics and Integrity': 'Ethics and Integrity - Overall Ranking',
            'Project Management': 'Project Management - Overall Ranking',
            'Transformational Leadership': 'Transformational Leadership - Overall Ranking',
            'Teamwork': 'Teamwork - Overall Ranking',
            'Intercultural Knowledge': 'Intercultural Knowledge - Overall Ranking'
        }
        
        visualization_type = st.selectbox(
            "Select Visualization Type",
            ["Overall Competency Rankings", "Subcompetency Analysis", "Relevance Code Analysis"]
        )
        
        if visualization_type == "Overall Competency Rankings":
            averages = calculate_competency_averages(df, competencies)
            fig = px.bar(
                x=list(averages.keys()),
                y=list(averages.values()),
                title="Overall Competency Rankings (Higher is Better)",
                labels={'x': 'Competency', 'y': 'Weighted Average Score'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
            
        elif visualization_type == "Subcompetency Analysis":
            selected_comp = st.selectbox("Select Competency", list(competencies.keys()))
            subcols = get_subcompetencies(df, selected_comp)
            
            if subcols:
                averages = {subcols[col]: calculate_weighted_average(df[col]) 
                           for col in subcols.keys()}
                fig = px.bar(
                    x=list(averages.keys()),
                    y=list(averages.values()),
                    title=f"Subcompetency Analysis for {selected_comp} (Higher is Better)",
                    labels={'x': 'Subcompetency', 'y': 'Weighted Average Score'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)
            
        else:  # Relevance Code Analysis
            selected_comp = st.selectbox("Select Competency", list(competencies.keys()))
            relcols = get_relevance_codes(df, selected_comp)
            
            if relcols:
                relevance_analysis = {}
                for col, display_name in relcols.items():
                    core_percent = (df[col] == 1).mean() * 100
                    diff_percent = (df[col] == 0).mean() * 100
                    relevance_analysis[display_name] = {
                        'Core': core_percent, 
                        'Differentiator': diff_percent
                    }
                
                fig = go.Figure()
                x_labels = list(relevance_analysis.keys())
                core_vals = [data['Core'] for data in relevance_analysis.values()]
                diff_vals = [data['Differentiator'] for data in relevance_analysis.values()]
                
                fig.add_trace(go.Bar(name='Core', x=x_labels, y=core_vals))
                fig.add_trace(go.Bar(name='Differentiator', x=x_labels, y=diff_vals))
                
                fig.update_layout(
                    barmode='stack',
                    title=f"Relevance Code Analysis for {selected_comp}",
                    xaxis_tickangle=-45,
                    yaxis_title="Percentage (%)"
                )
                st.plotly_chart(fig)
                
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
