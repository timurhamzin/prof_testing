import plotly.express as px
import streamlit as st

from score import run_mock_test


def tree_view(data, parent_name="", level=0):
    for key, value in data.items():
        if type(value) == dict:
            if level == 0:
                with st.expander(key):  # Use as a context manager only at the top level
                    tree_view(value, key, level + 1)
            else:
                st.write(f"{'--' * level} {key}")  # Use simple text for nested keys
                tree_view(value, key, level + 1)
        else:
            st.write(f"{'--' * level} {parent_name}/{key}: {value}")


def adjust_subcategory_scores(data):
    for dimension, categories in data.items():
        for category, subcategories in categories.items():
            total = subcategories.get("total", 0)
            subcategories_sum = sum([score for subcat, score in subcategories.items() if subcat != "total"])

            # Check if subcategories sum is not zero to avoid division by zero
            if subcategories_sum != 0:
                factor = total / subcategories_sum
                for subcategory, score in subcategories.items():
                    if subcategory != "total":
                        subcategories[subcategory] = score * factor
                    else:
                        subcategories[subcategory] = score

            # If there's no subcategories, just distribute the total equally among them
            else:
                num_subcats = len(subcategories) - 1  # Exclude the "total" subcategory
                if num_subcats:
                    equal_val = total / num_subcats
                    for subcategory in subcategories.keys():
                        if subcategory != "total":
                            subcategories[subcategory] = equal_val

    return data


def visualize_scores(result_scores, columns=3, show_zero_scores=True):
    num_rows = -(-len(result_scores) // columns)  # Equivalent to math.ceil(len(result_scores) / 2)
    col_pairs = []

    for _ in range(num_rows):
        col_pairs.append(st.columns(columns))

    cols = [col for pair in col_pairs for col in pair]

    for col, (dimension, categories) in zip(cols, result_scores.items()):
        ids = []
        labels = []
        parents = []
        values = []
        ids.append(dimension)
        labels.append(dimension)
        parents.append('')
        root_value = sum([subcategories.get("total", 0) for _, subcategories in categories.items()])
        values.append(root_value)  # Set root node value to 0

        for category, subcategories in categories.items():
            ids.append(f"{dimension}-{category}")
            labels.append(category)
            parents.append(dimension)
            total_value = subcategories.get("total", 0)  # Get the "total" value for the category
            values.append(total_value)  # Use the "total" value for the category width

            for subcategory, score in subcategories.items():
                if subcategory == "total":
                    continue  # Skip the "total" key for subcategories
                if score == 0 and not show_zero_scores:
                    continue  # Skip zero scores if not showing them

                ids.append(f"{dimension}-{category}-{subcategory}")
                labels.append(subcategory)
                parents.append(f"{dimension}-{category}")
                values.append(score)  # Add the score as the value for the subcategory

        # print('sunburst kwargs: ', json.dumps(
        #     dict(
        #         names=labels,
        #         ids=ids,
        #         parents=parents,
        #         values=values,  # Updated values parameter
        #     ), indent=2
        # ))

        fig = px.sunburst(
            names=labels,
            ids=ids,
            parents=parents,
            values=values,  # Updated values parameter
            title=f"{dimension}".capitalize(),
            branchvalues='total'
        )
        col.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    # You can load result_scores from score.py or any other source
    raw_test_results = run_mock_test()
    adjusted_scores = adjust_subcategory_scores(raw_test_results)
    st.title("Vocational Placement Test Results")
    # print('result_scores = ', json.dumps(result_scores, indent=2))
    # tree_view(result_scores)
    visualize_scores(adjusted_scores, show_zero_scores=True)
