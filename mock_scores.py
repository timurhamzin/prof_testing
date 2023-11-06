from score import ProfilingTestScoring, adjust_subcategory_scores
from utils import load_and_merge_questions, load_answers, export_results


def collect_mock_results(export=False):
    """Run a profiling test on mock questions and answers to generate result scores."""
    questions_table = load_and_merge_questions()
    answers_table = load_answers()
    scorer = ProfilingTestScoring(user_id=123, questions=questions_table, user_answers=answers_table)
    result_scores = scorer.calculate_scores_for_profiling_test()
    if export:
        adjusted_scores = adjust_subcategory_scores(result_scores)
        export_results(questions_table, answers_table, result_scores, adjusted_scores)
    return result_scores


if __name__ == '__main__':
    collect_mock_results()
