import json
from collections import defaultdict, Counter
from pathlib import Path

DEBUG = False

class VocationalScoring:

    def __init__(self, user_id):
        self.user_id = user_id
        self.total_scores = {}

    def fetch_answers(self):
        return fetch_answers_for_user(self.user_id)

    def get_or_init(self, dictionary, key, default=0):
        if key not in dictionary:
            dictionary[key] = default
        return dictionary[key]

    def process_score(self, dimension, category, subcategory, score):
        # global DEBUG
        # if DEBUG:
        #     pdb.set_trace()
        #     DEBUG = False
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
            self.total_scores[dimension][category]['total'] = self.total_scores[dimension][category].get('total',
                                                                                                         0) + score
        else:
            if subcategory not in self.total_scores[dimension][category]:
                self.total_scores[dimension][category][subcategory] = 0
            self.total_scores[dimension][category][subcategory] += score

    def process_option(self, option, question, is_correct=True):
        scorings = question['scoring_details'].get(option, [])
        for scoring in scorings:
            dimension = scoring.get('dimension')
            category = scoring.get('category')
            subcategory = scoring.get('subcategory')
            score = scoring.get('score', 0)
            if not is_correct and 'negative_score' in scoring:
                score = scoring.get('negative_score')
            self.process_score(dimension, category, subcategory, score)

    def calculate_scores(self):
        user_answers = self.fetch_answers()
        for answer in user_answers:
            question = fetch_question_by_id(answer['question_id'])
            # if not question:
            #     id = answer['question_id']
            #     print(f'Question with id {id} is missing. Looking at question examples below, reconstruct it based on this answer: {answer}')
            #     continue
            # elif not question['answer_structure']:
            #     id = answer['question_id']
            #     print(f'Question with id {id} is missing answer_structure. Looking at question examples below, reconstruct it based on this answer: {answer}')
            #     continue
            # if answer['question_id'] == 105:
            #     global DEBUG
            #     DEBUG = True
            if question['answer_structure']['type'] in ['multiple', 'single']:
                for option in answer['answer'].get('selected', []):
                    self.process_option(option, question)
            elif question['answer_structure']['type'] == 'open':
                pass
            elif question['answer_structure']['type'] == 'list-matching':
                for option, selected_value in answer['answer'].items():
                    if selected_value == question['answer_structure']['pairs'][option]:
                        self.process_option(option, question, is_correct=True)
                    else:
                        self.process_option(option, question, is_correct=False)
        return self.total_scores


def fetch_question_by_id(question_id):
    return next((q for q in questions_table if q["id"] == question_id), None)


def fetch_answers_for_user(user_id):
    return [answer for answer in answers_table if answer["user_id"] == user_id]


def rate_open_question(text):
    # This is a mock implementation. Typically, this would use NLP or some heuristic to rate the answer.
    if "break problems" in text:
        return {"analytical": 2}
    return {}

def load_and_merge_questions():
    merged_questions = []
    dimensions_folder = Path("mock_prof_test/questions")
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


def load_answers():
    answers_fpath = Path("mock_prof_test/answers/answers.json")
    with open(answers_fpath, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_mock_test():
    global questions_table
    global answers_table
    questions_table = load_and_merge_questions()
    answers_table = load_answers()
    # answers_table = [answer for answer in load_answers() if answer['id'] == 204]
    # answers_table = [answer for answer in load_answers() if 'academics' in str(answer)]
    with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/questions_table.json', 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(questions_table, ensure_ascii=False))
    with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/answers_table.json', 'w',encoding='utf-8') as fh:
        fh.write(json.dumps(answers_table, ensure_ascii=False))
    scorer = VocationalScoring(user_id=123)
    result_scores = scorer.calculate_scores()
    with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/result_scores.json', 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(result_scores, ensure_ascii=False))
    return result_scores


if __name__ == "__main__":
    run_mock_test()