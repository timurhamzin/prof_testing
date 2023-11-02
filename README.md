# Profiling Test Application with Streamlit

## Overview

This project is a web-based application for conducting profiling tests using Streamlit. It offers a way to display questions, gather user responses, and visualize the results. Answers are scored across multiple subcategories, categories and dimensions, which are visualized in sunburst charts, one for each dimension.
The system is modularized into four main Python files:

- `questionnaire.py`: The main script for running the Streamlit app, responsible for handling UI interactions and maintaining session state.
- `score.py`: Contains the `ProfilingTestScoring` class, which calculates the test scores based on user responses.
- `utils.py`: Provides utility functions for loading and merging questions from JSON files, fetching answers, and exporting results.
- `visualize.py`: Functions to visualize the test results using Plotly.

## Installation

1. Install dependencies into your active virtual environment, e.g.:

    ```bash
    pip install -r requirements.txt
    ```

2. Clone the repository to your local machine:

    ```bash
    git clone <repository_url>
    ```

3. Navigate to the project directory:

    ```bash
    cd /path/to/univero/prof_testing
    ```

## Usage

1. Run the Streamlit app:

    ```bash
    streamlit run questionnaire.py
    ```

2. Navigate to the URL provided in the terminal to interact with the application.

## Directory Structure

```
...
└── prof_testing
    ├── questionnaire.py
    ├── score.py
    ├── utils.py
    └── visualize.py
```

## Features

### Questionnaire

- Supports different types of questions: single choice, multiple choice, and list matching.
- Navigation between questions.
- Validation of session states.

### Scoring

- Uses a scoring mechanism defined in the `ProfilingTestScoring` class.
- Supports different question types.

### Utility Functions

- Loading and merging questions from various dimensions.
- Exporting test results.

### Visualization

- Uses Plotly to create sunburst charts for visualizing the test scores.

## Debugging

Pass the `debug=true` query parameter in the URL to enable the debug mode, which displays additional details and visualizes test results on the fly.
Pass `filter` argument to filter questions, e.g. filter=single,multiple to display only questions of `single` and `multiple` types.

## API

Please refer to the inline comments and docstrings in each Python file for more details about the classes and functions.

## Contributing

To contribute to this project, please follow the usual fork, feature-branch, pull-request workflow.

## License

This project is licensed under the MIT License.

## Contact

For more information, please contact the repository owner.
