import streamlit as st
import json
from score import load_and_merge_questions, VocationalScoring

questions_table = load_and_merge_questions()

with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/questions_table.json', 'w', encoding='utf-8') as fh:
    fh.write(json.dumps(questions_table, ensure_ascii=False))

st.session_state["current_question_index"] = st.session_state.get("current_question_index", 0)

with st.container():
    question = questions_table[st.session_state["current_question_index"]]
    st.write(question["question_text"])

    if question["question_type"] in ["single", "multiple"]:
        stored_index_key = f"stored_answer_index_{st.session_state['current_question_index']}"
        stored_index = st.session_state.get(stored_index_key, 0)
        answer = st.radio("Select an option:", question["options"], index=stored_index, key=f"answer_{st.session_state['current_question_index']}")
        selected_index = question["options"].index(answer) if answer in question["options"] else 0
        st.session_state[f"stored_answer_index_{st.session_state['current_question_index']}"] = selected_index

    elif question["question_type"] == "list-matching":
        # Create inner container for list-matching questions
        with st.container():
            answer = {}
            for option in question["options"]:
                stored_index_key = f"stored_answer_index_{option}"
                stored_index = st.session_state.get(stored_index_key, 0)
                col1, col2 = st.columns(2)  # Split into two columns
                col1.write(f"Match {option} with:")
                selected_answer = col2.selectbox("", question["answer_structure"]["options"], index=stored_index, key=f"answer_{option}")
                answer[option] = selected_answer

                selected_index = question["answer_structure"]["options"].index(selected_answer) if selected_answer in question["answer_structure"]["options"] else 0
                st.session_state[stored_index_key] = selected_index
    else:
        raise AssertionError(f'Question type `{question["question_type"]}` is undefined.')

    st.session_state[f"stored_answer_{st.session_state['current_question_index']}"] = answer

with st.container():
    col1, col2, col3 = st.columns([1, 0.4, 1])
    # col2.button("Previous")
    # col3.button("Next")
    if col2.button("Previous", key="previous_button") and st.session_state["current_question_index"] > 0:
        st.session_state["current_question_index"] -= 1
        st.rerun()
    if col3.button("Next", key="next_button") and st.session_state["current_question_index"] < len(questions_table) - 1:
        st.session_state["current_question_index"] += 1
        st.rerun()


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
                    # This is a simplified scoring mechanism, you may need to adjust this to match your scoring logic
                    "scoring_details": questions_table[i]["scoring_details"]
                }
            }
            answers_table.append(answer_dict)
    return answers_table


# print(fetch_answers_for_user(user_id=123))


if st.session_state["current_question_index"] == len(questions_table) - 1 and st.button("Submit"):
    answers_table = fetch_answers_for_user(user_id=123)
    with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/answers_table.json', 'w',encoding='utf-8') as fh:
        fh.write(json.dumps(answers_table, ensure_ascii=False))

    scorer = VocationalScoring(user_id=123, questions=questions_table, user_answers=answers_table)
    result_scores = scorer.calculate_scores()

    with open('/home/timur/Work/univero/prof_testing/mock_prof_test/example_output/result_scores.json', 'w',
              encoding='utf-8') as fh:
        fh.write(json.dumps(result_scores, ensure_ascii=False))
