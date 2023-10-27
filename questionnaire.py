import streamlit as st
import json

from plot import adjust_subcategory_scores, visualize_scores
from score import load_and_merge_questions, VocationalScoring

questions_table = load_and_merge_questions()
questions_table = [q for q in questions_table if 'Anthropology' in str(q)]

with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/questions_table.json', 'w',
          encoding='utf-8') as fh:
    fh.write(json.dumps(questions_table, ensure_ascii=False))

st.session_state["current_question_index"] = st.session_state.get("current_question_index", 0)

with st.container():
    col1, col2, col3 = st.columns([1, 2, 1])
    if col1.button("Previous") and st.session_state["current_question_index"] > 0:
        st.session_state["current_question_index"] -= 1
        st.rerun()
    if col3.button("Next") and st.session_state["current_question_index"] < len(questions_table) - 1:
        st.session_state["current_question_index"] += 1
        st.rerun()
    # with st.container():
    question = questions_table[st.session_state["current_question_index"]]
    col2.write(question["question_text"])

    if question["question_type"] in ["single", "multiple"]:
        stored_index_key = f"stored_answer_index_{st.session_state['current_question_index']}"
        stored_index = st.session_state.get(stored_index_key, 0)
        answer = col2.radio("Select an option:", question["options"], index=stored_index,
                            key=f"answer_{st.session_state['current_question_index']}")
        selected_index = question["options"].index(answer) if answer in question["options"] else 0
        st.session_state[f"stored_answer_index_{st.session_state['current_question_index']}"] = selected_index

    elif question["question_type"] == "list-matching":
        answer = {}
        for option in question["options"]:
            stored_index_key = f"stored_answer_index_{option}"
            stored_index = st.session_state.get(stored_index_key, 0)
            selected_answer = col2.selectbox(f"Match {option} with:", question["answer_structure"]["options"],
                                             index=stored_index, key=f"answer_{option}")
            answer[option] = selected_answer

            selected_index = question["answer_structure"]["options"].index(selected_answer) if selected_answer in \
                                                                                               question[
                                                                                                   "answer_structure"][
                                                                                                   "options"] else 0
            st.session_state[stored_index_key] = selected_index
    else:
        raise AssertionError(f'Question type `{question["question_type"]}` is undefined.')

    st.session_state[f"stored_answer_{st.session_state['current_question_index']}"] = answer


def fetch_answers_for_user(user_id):
    answers_table = []
    for i in range(len(questions_table)):
        if f"stored_answer_{i}" in st.session_state:
            answer_dict = {
                "id": i + 1,  # Assuming id starts from 1 and increments sequentially
                "user_id": user_id,
                "question_id": questions_table[i]["id"],
                "answer": {
                    "selected": st.session_state[f"stored_answer_{i}"],
                    "scoring_details": questions_table[i]["scoring_details"],
                    "question_type": questions_table[i]["question_type"]
                }
            }
            answers_table.append(answer_dict)
    return answers_table


# print(fetch_answers_for_user(user_id=123))


if st.session_state["current_question_index"] == len(questions_table) - 1 and st.button("Submit"):
    answers_table = fetch_answers_for_user(user_id=123)
    with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/answers_table.json', 'w',
              encoding='utf-8') as fh:
        fh.write(json.dumps(answers_table, ensure_ascii=False))

    scorer = VocationalScoring(user_id=123, questions=questions_table, user_answers=answers_table)
    result_scores = scorer.calculate_scores()
    # print('result_scores =', result_scores)

    with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/result_scores.json', 'w',
              encoding='utf-8') as fh:
        fh.write(json.dumps(result_scores, ensure_ascii=False))
    adjusted_scores = adjust_subcategory_scores(result_scores)
    st.title("Vocational Placement Test Results")
    # print('adjusted_scores =', adjusted_scores)
    visualize_scores(adjusted_scores, show_zero_scores=True)

    extracted_answers = []
    for answer in answers_table:
        if scorer.fetch_question_by_id(answer['question_id'])["question_type"] == "list-matching":
            extracted_answers.append(answer)
    # print(json.dumps(extracted_answers, indent=2))
    print(json.dumps(result_scores, indent=2))
