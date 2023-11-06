"""
This module contains the function to visualize test scores using Streamlit and Plotly.

Functions:
    visualize_adjusted_scores(result_scores: Dict, columns: int = 3, show_zero_scores: bool = True) -> None
"""

import plotly.express as px
import streamlit as st

from mock_scores import collect_mock_results
from score import adjust_subcategory_scores


def visualize_adjusted_scores(result_scores, columns=3, show_zero_scores=True):
    """
    Visualize test scores using a sunburst chart.

    Parameters:
        result_scores (Dict): A dictionary containing the test scores for different dimensions and categories.
        columns (int, optional): The number of columns for displaying the charts. Defaults to 3.
        show_zero_scores (bool, optional): Whether to show categories with zero scores. Defaults to True.
    """
    num_rows = -(-len(result_scores) // columns)
    col_pairs = [st.columns(columns) for _ in range(num_rows)]
    cols = [col for pair in col_pairs for col in pair]

    for (col, (dimension, categories)) in zip(cols, result_scores.items()):
        ids, labels, parents, values = [], [], [], []
        ids.append(dimension)
        labels.append(dimension)
        parents.append('')
        root_value = sum([subcategories.get('total', 0) for _, subcategories in categories.items()])
        values.append(root_value)

        for category, subcategories in categories.items():
            ids.append(f'{dimension}-{category}')
            labels.append(category)
            parents.append(dimension)
            total_value = subcategories.get('total', 0)
            values.append(total_value)

            for subcategory, score in subcategories.items():
                if subcategory == 'total' or (score == 0 and not show_zero_scores):
                    continue
                ids.append(f'{dimension}-{category}-{subcategory}')
                labels.append(subcategory)
                parents.append(f'{dimension}-{category}')
                values.append(score)

        fig = px.sunburst(
            names=labels, ids=ids, parents=parents, values=values,
            title=f'{dimension}'.capitalize(), branchvalues='total'
        )
        col.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    raw_test_results = collect_mock_results()
    adjusted_scores = adjust_subcategory_scores(raw_test_results)
    st.title('Profiling Test Results')
    visualize_adjusted_scores(adjusted_scores, show_zero_scores=True)
