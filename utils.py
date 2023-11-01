"""
This module contains utility functions to load and manage profiling test data.
"""

import json
import os
from pathlib import Path
from typing import List, Dict

from config import MOCK_PROFTEST_DIR


def fetch_answers_for_user(user_id: int, answers_table: List[Dict]) -> List[Dict]:
    """Fetch answers for a specific user."""
    return [answer for answer in answers_table if answer['user_id'] == user_id]


def rate_open_question(text: str) -> Dict[str, int]:
    """Rate an open question based on the text."""
    # This is a mock implementation. Typically, this would use NLP or some heuristic to rate the answer.
    if 'break problems' in text:
        return {'analytical': 2}
    return {}


def load_and_merge_questions() -> List[Dict]:
    """Load and merge questions from different dimensions."""
    merged_questions = []
    dimensions_folder = Path(f'{MOCK_PROFTEST_DIR}/questions')
    for dimension_folder in dimensions_folder.iterdir():
        if dimension_folder.is_dir():
            category_path = dimension_folder / 'category.json'
            subcategory_path = dimension_folder / 'subcategory.json'
            if category_path.exists():
                with open(category_path, 'r') as f:
                    category_questions = json.load(f)
                    merged_questions.extend(category_questions)
            if subcategory_path.exists():
                with open(subcategory_path, 'r') as f:
                    subcategory_questions = json.load(f)
                    merged_questions.extend(subcategory_questions)
    return merged_questions


def load_answers() -> List[Dict]:
    """Load answers from a JSON file."""
    answers_fpath = Path('mock_prof_test/example_data/answers_table.json')
    with open(answers_fpath, 'r', encoding='utf-8') as f:
        return json.load(f)


def export_results(questions_table, answers_table, result_scores, adjusted_scores=None):
    """Export test data and results to JSON files."""
    export_dir = os.path.join(MOCK_PROFTEST_DIR, 'example_data')
    with open(os.path.join(export_dir, 'questions_table.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(questions_table, ensure_ascii=False))
    with open(os.path.join(export_dir, 'answers_table.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(answers_table, ensure_ascii=False))
    with open(os.path.join(export_dir, 'result_scores.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(result_scores, ensure_ascii=False))
    if adjusted_scores:
        with open(os.path.join(export_dir, 'adjusted_scores.json'), 'w', encoding='utf-8') as fh:
            fh.write(json.dumps(adjusted_scores, ensure_ascii=False))
