import copy
import json
import os

import streamlit as st

from plot import adjust_subcategory_scores, visualize_scores
from score import load_and_merge_questions, VocationalScoring


def rerun_script():
    st.rerun()


def validate_current_question_index():
    index = st.session_state.get("current_question_index", 0)
    max_index = len(questions_table) - 1
    if index < 0 or index > max_index:
        if max_index <= 0:
            st.error("There are no questions for you query, try changing the filter value.")
        else:
            st.error("Invalid current question index. Resetting to 0.")
            st.session_state["current_question_index"] = 0
            rerun_script()


def validate_session_state(key, expected_type, valid_range=None):
    try:
        value = st.session_state.get(key, None)
        if value is None:
            return True

        if not isinstance(value, expected_type):
            raise ValueError(f"Invalid type for key '{key}'. Expected {expected_type}.")

        if valid_range is not None and value not in valid_range:
            raise ValueError(f"Invalid range for key '{key}'. Should be in {valid_range}.")

    except ValueError as e:
        st.error(f"Error with key '{key}' in session state: {e}")
        return False

    return True


def fetch_answers_for_user(user_id, stored_answer_key=None):
    answers_table = []
    for question in questions_table:
        question_id = question['id']
        question_type = question['question_type']
        if question_type == 'list-matching':
            # Create a dictionary to store all selected values for different options
            if stored_answer_key is not None and stored_answer_key != stored_answer_key:
                continue
            selected_answers = {}
            for option in question['options']:
                stored_option_key = get_stored_answer_key(f'{question_id}_{option}')
                if stored_option_key in st.session_state:
                    selected_answers[option] = st.session_state[stored_option_key]
            # Append the combined answer dictionary to answers_table for list-matching question type
            if selected_answers:
                answer_dict = {'id': question_id, 'user_id': user_id, 'test_id': 0, 'question_id': question_id, 'answer': {'selected': selected_answers, 'scoring_details (FOR DEBUG ONLY)': question['scoring_details']}}
                answers_table.append(answer_dict)
                if stored_answer_key is not None and stored_answer_key == get_stored_answer_key(question_id):
                    return answers_table
        elif question_type in ['single', 'multiple']:
            stored_option_key = get_stored_answer_key(question_id)
            if stored_answer_key is not None and stored_option_key != stored_answer_key:
                continue
            if stored_option_key in st.session_state:
                answer_dict = {'id': question_id, 'user_id': user_id, 'test_id': 0, 'question_id': question_id, 'answer': {'selected': st.session_state[stored_option_key], 'scoring_details (FOR DEBUG ONLY)': question['scoring_details']}}
                answers_table.append(answer_dict)
                if stored_answer_key is not None:
                    return answers_table
        else:
            raise ValueError(f'Illegal value for question type: `{question_type}`.')
    return answers_table


def get_stored_answer_key(question_id):
    return f"answer_for_question_{question_id}"


def handle_single_question(question, col):
    global answer
    question_id = question["id"]
    stored_answer_key = get_stored_answer_key(question_id)
    if stored_answer_key not in st.session_state:
        st.session_state[stored_answer_key] = 0  # Initialize

    stored_answer = st.session_state[stored_answer_key]

    answer = col.radio(
        "Select an option:", question["options"],
        index=stored_answer,
        key=f"answer_{question_id}"
    )

    new_answer_index = question["options"].index(answer)
    if new_answer_index != stored_answer:
        st.session_state[stored_answer_key] = new_answer_index
        st.rerun()
    return answer


def handle_multiple_question(question, col2):
    question_id = question['id']
    stored_answer_key = get_stored_answer_key(question_id)
    if not validate_session_state(stored_answer_key, list):
        return
    stored_indices = st.session_state.get(stored_answer_key, [])
    answer = col2.multiselect(
        "Select one or more options:", question["options"],
        default=[question["options"][i] for i in stored_indices],
        key=f"answer_{question_id}"
    )

    new_answer_indices = [question["options"].index(opt) for opt in answer]
    if new_answer_indices != stored_indices:
        st.session_state[stored_answer_key] = new_answer_indices
        st.rerun()
    return answer


def handle_list_matching_question(question, col2):
    answer = {}
    for option in question['options']:
        question_id = question["id"]
        stored_answer_key = get_stored_answer_key(f"{question_id}_{option}")

        if not validate_session_state(stored_answer_key, int, range(len(question['answer_structure']['options']))):
            continue
        stored_index = st.session_state.get(stored_answer_key, 0)

        selected_answer = col2.selectbox(
            f'Match {option} with:',
            question['answer_structure']['options'],
            index=stored_index,
            key=f"answer_{question_id}_{option}"
        )

        new_answer_index = question['answer_structure']['options'].index(selected_answer)
        if new_answer_index != stored_index:
            st.session_state[stored_answer_key] = new_answer_index
            st.rerun()

        answer[option] = selected_answer
        st.session_state[stored_answer_key] = question['answer_structure']['options'].index(selected_answer)

    return answer


st.set_page_config(layout='wide')

# Fetch query parameters
query_params = st.experimental_get_query_params()

# Set DEBUG from query parameters
DEBUG = query_params.get('debug', [False])[0]
if isinstance(DEBUG, str) and DEBUG.lower() == 'true':
    DEBUG = True
elif isinstance(DEBUG, str) and DEBUG.lower() == 'false':
    DEBUG = False

filter_param = query_params.get('filter', [''])[0]  # default to an empty string
filter = filter_param.split(',')
if isinstance(filter, list):  # Ensure it's a list
    filter = [str(f) for f in filter]  # Convert all to string just in case

questions_table = load_and_merge_questions()
if filter:
    questions_table = [q for q in questions_table if any(f in str(q) for f in filter)]

validate_current_question_index()

BASE_DIR = 'mock_prof_test'

with open(os.path.join(BASE_DIR, 'example_output', 'questions_table.json'), 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(questions_table, ensure_ascii=False))

st.session_state["current_question_index"] = st.session_state.get("current_question_index", 0)

st.markdown('<style>.small-font pre { font-size: 12px; }</style>', unsafe_allow_html=True)

with st.container():
    col0, col1, col2, col3, col4 = st.columns([2, 1, 2, 1, 2])

    if DEBUG and 'current_question_index' in st.session_state:
        current_question = copy.deepcopy(questions_table[st.session_state['current_question_index']])
        del current_question["scoring_details"]
        question_data = json.dumps(current_question, indent=2, ensure_ascii=False)
        col0.code(f"Input: {question_data}", language="json")

    if col1.button("Previous") and st.session_state["current_question_index"] > 0:
        st.session_state["current_question_index"] -= 1
        validate_current_question_index()  # Add this line
        rerun_script()

    if col3.button("Next") and st.session_state["current_question_index"] < len(questions_table) - 1:
        st.session_state["current_question_index"] += 1
        validate_current_question_index()  # Add this line
        rerun_script()

    question: dict = questions_table[st.session_state["current_question_index"]]
    col2.write(question["question_text"])

    if question["question_type"] == "single":
        answer = handle_single_question(question, col2)
    elif question["question_type"] == "multiple":
        answer = handle_multiple_question(question, col2)
    elif question["question_type"] == "list-matching":
        answer = handle_list_matching_question(question, col2)
    else:
        raise AssertionError(f'Question type `{question["question_type"]}` is undefined.')

    # st.session_state[f"stored_answer_{st.session_state['current_question_index']}"] = answer

if DEBUG:
    debug_answers = fetch_answers_for_user(user_id=123, stored_answer_key=get_stored_answer_key(question["id"]))
    debug_answers_text = json.dumps(debug_answers, indent=2, ensure_ascii=False)
    col4.code(f"Output - Answers: {debug_answers_text}", language="json")

if ((st.session_state["current_question_index"] == len(questions_table) - 1) and st.button("Submit")) or DEBUG:
    answers_table = fetch_answers_for_user(user_id=123)
    with open(os.path.join(BASE_DIR, 'example_output', 'answers_table.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(answers_table, ensure_ascii=False))

    scorer = VocationalScoring(user_id=123, questions=questions_table, user_answers=answers_table)
    result_scores = scorer.calculate_scores_for_profiling_test()
    # print('result_scores =', result_scores)

    with open(os.path.join(BASE_DIR, 'example_output', 'result_scores.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(result_scores, ensure_ascii=False))
    adjusted_scores = adjust_subcategory_scores(result_scores)
    with open(os.path.join(BASE_DIR, 'example_output', 'adjusted_scores.json'), 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(result_scores, ensure_ascii=False))
    st.title("Vocational Placement Test Results")
    # print('adjusted_scores =', adjusted_scores)
    visualize_scores(adjusted_scores, show_zero_scores=True)

    extracted_answers = []
    for answer in answers_table:
        if scorer.fetch_question_by_id(answer['question_id'])["question_type"] == "list-matching":
            extracted_answers.append(answer)
    # print(json.dumps(extracted_answers, indent=2))
    print('result_scores', json.dumps(result_scores, indent=2))
    print('adjusted_scores', json.dumps(adjusted_scores, indent=2))
