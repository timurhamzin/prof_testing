"""
This module contains the ProfilingTestScoring class responsible for calculating profiling test scores.
"""
import json
from typing import List, Dict, Optional


class ProfilingTestScoring:
    """
    A class to represent the scoring mechanism for profiling tests.

    Attributes:
        user_id (int): ID of the user taking the test.
        questions (List[Dict]): List of questions in the test.
        user_answers (List[Dict]): List of user answers.
        total_scores (Dict): A nested dictionary to hold the total scores.
    """

    def __init__(self, user_id: int, questions: List[Dict], user_answers: List[Dict]):
        """Initialize a ProfilingTestScoring object."""
        self.user_id = user_id
        self.total_scores = {}
        self.questions = questions
        self.user_answers = user_answers

    def process_score(self, dimension: str, category: Optional[str], subcategory: Optional[str], score: int):
        """Process and update the scores for a given dimension, category, and subcategory."""
        if not all([dimension, category, score]):
            return

        if dimension not in self.total_scores:
            self.total_scores[dimension] = {}

        if not category:
            self.total_scores[dimension]['total'] = self.total_scores[dimension].get('total', 0) + score
            return

        if category not in self.total_scores[dimension]:
            self.total_scores[dimension][category] = {}

        if not subcategory:
            self.total_scores[dimension][category]['total'] = (
                    self.total_scores[dimension][category].get('total', 0) + score)
        else:
            if subcategory not in self.total_scores[dimension][category]:
                self.total_scores[dimension][category][subcategory] = 0
            self.total_scores[dimension][category][subcategory] += score

    def process_option(self, question: Dict, *, is_correct: bool = True, option_index: Optional[int] = None,
                       or_option_value: Optional[str] = None):
        """Process the scoring for a given question option."""
        if option_index is not None:
            scorings = question['scoring_details'].get(question['answer_structure']['options'][option_index], [])
        elif or_option_value is not None:
            scorings = question['scoring_details'].get(or_option_value, [])
        else:
            assert False, 'Either `option_index` or `or_option_value` must be set.'

        for scoring in scorings:
            dimension = scoring.get('dimension')
            category = scoring.get('category')
            subcategory = scoring.get('subcategory')
            score = 0
            if is_correct:
                score = scoring.get('score', 0)
            elif 'negative_score' in scoring:
                score = scoring.get('negative_score')
            self.process_score(dimension, category, subcategory, score)

    def fetch_question_by_id(self, question_id: int) -> Optional[Dict]:
        """Fetch a question by its ID."""
        return next((q for q in self.questions if q['id'] == question_id), None)

    def calculate_scores_for_profiling_test(self) -> Dict:
        """Calculate the total scores for a profiling test."""
        for answer in self.user_answers:
            question = self.fetch_question_by_id(answer['question_id'])
            if question['question_type'] in ['multiple', 'single']:
                selected_options = answer['answer'].get('selected')
                if isinstance(selected_options, list):
                    for option_index in selected_options:
                        self.process_option(question, is_correct=True, option_index=option_index)
                elif isinstance(selected_options, int):
                    option_index = selected_options
                    self.process_option(question, is_correct=True, option_index=option_index)
            elif question['question_type'] == 'open':
                raise NotImplemented('Implement logic for `open` questions in `calculate_scores_for_profiling_test`')
            elif question['question_type'] == 'list-matching':
                correct_pairs = question['scoring_details'].get('correct_pairs', {})
                for option_value, selected_index in answer['answer']['selected'].items():
                    selected_value = question['answer_structure']['options'][selected_index]
                    correct_value = correct_pairs.get(option_value)
                    if correct_value is not None and selected_value == correct_value:
                        self.process_option(question, is_correct=True, or_option_value=option_value)
                    else:
                        self.process_option(question, is_correct=False, or_option_value=option_value)
        return self.total_scores


def adjust_subcategory_scores(data):
    for dimension, categories in data.items():
        # Check if either all categories have the 'total' key or none of them have it
        total_keys_count = sum(1 for category, subcategories in categories.items() if 'total' in subcategories)
        if total_keys_count not in [0, len(categories)]:
            raise ValueError(
                (f'Inconsistent \'total\' keys in categories for dimension `{dimension}`. '
                 'Either all categories should have the \'total\' key or none of them should.'
                 f'Violating categories: \n{json.dumps(categories, indent=2)}'))

        for category, subcategories in categories.items():
            subcategories_sum = sum([score for subcat, score in subcategories.items() if subcat != 'total'])
            total = subcategories.get('total', subcategories_sum)

            # Check if subcategories sum is not zero to avoid division by zero
            if subcategories_sum != 0:
                factor = total / subcategories_sum
                for subcategory, score in subcategories.items():
                    if subcategory != 'total':
                        subcategories[subcategory] = score * factor
                    else:
                        subcategories[subcategory] = score

                subcategories['total'] = sum([score for subcat, score in subcategories.items() if subcat != 'total'])
            # If there's no subcategories, just distribute the total equally among them
            else:
                num_subcats = len(subcategories) - (
                    1 if 'total' in subcategories else 0)  # Exclude the 'total' subcategory
                if num_subcats:
                    equal_val = (total or num_subcats) / num_subcats
                    for subcategory in subcategories.keys():
                        if subcategory != 'total':
                            subcategories[subcategory] = equal_val
                    subcategories['total'] = sum(
                        [score for subcat, score in subcategories.items() if subcat != 'total'])

    return data
