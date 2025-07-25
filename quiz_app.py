import streamlit as st
import sqlite3
import datetime
import pandas as pd

# --- Database Functions1 ---

def init_db():
    """Initializes the database and creates the results table if it doesn't exist."""
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    # Create table to store quiz results
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            timestamp DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_result(name, score, total_questions):
    """Adds a quiz result to the database."""
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    timestamp = datetime.datetime.now()
    c.execute("INSERT INTO results (name, score, total_questions, timestamp) VALUES (?, ?, ?, ?)",
              (name, score, total_questions, timestamp))
    conn.commit()
    conn.close()

def get_all_results():
    """Retrieves all results from the database, ordered by score."""
    conn = sqlite3.connect('quiz_results.db')
    c = conn.cursor()
    c.execute("SELECT name, score, total_questions, timestamp FROM results ORDER BY score DESC, timestamp DESC")
    results = c.fetchall()
    conn.close()
    return results

# --- Quiz Content ---

quiz_questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": "Paris"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars"
    },
    {
        "question": "What is the largest mammal in the world?",
        "options": ["Elephant", "Blue Whale", "Giraffe", "Great White Shark"],
        "answer": "Blue Whale"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"],
        "answer": "William Shakespeare"
    },
    {
        "question": "What is the value of pi (π) to two decimal places?",
        "options": ["3.12", "3.14", "3.16", "3.18"],
        "answer": "3.14"
    }
]

# --- Streamlit App ---

def main():
    st.set_page_config(page_title="Online Quiz", page_icon="❓")

    # Initialize the database on first run
    init_db()

    st.title("🚀 Online Quiz Challenge!")
    st.write("Test your knowledge with our fun quiz. Enter your name and get started!")

    # Use session state to manage the quiz's flow
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.quiz_submitted = False
        st.session_state.user_name = ""
        st.session_state.user_answers = {}
        st.session_state.result_saved = False

    # Screen 1: Start Screen
    if not st.session_state.quiz_started:
        name = st.text_input("Enter your name to begin:", key="name_input")
        if st.button("Start Quiz"):
            if name:
                st.session_state.user_name = name
                st.session_state.quiz_started = True
                st.rerun()
            else:
                st.warning("Please enter your name to start the quiz.")
    # Screen 2: Quiz in Progress
    elif not st.session_state.quiz_submitted:
        st.write(f"Good luck, **{st.session_state.user_name}**!")
        with st.form(key='quiz_form'):
            user_answers = {}
            for i, q in enumerate(quiz_questions):
                st.subheader(f"Question {i+1}: {q['question']}")
                user_answers[i] = st.radio("Choose your answer:", q['options'], key=f"q_{i}", index=None)
            
            if st.form_submit_button(label='Submit Answers'):
                if all(answer is not None for answer in user_answers.values()):
                    st.session_state.user_answers = user_answers
                    st.session_state.quiz_submitted = True
                    st.rerun()
                else:
                    st.error("Please answer all questions before submitting.")
    # Screen 3: Results Screen
    else:
        score = sum(1 for i, q in enumerate(quiz_questions) if st.session_state.user_answers.get(i) == q['answer'])
        total = len(quiz_questions)

        if not st.session_state.result_saved:
            add_result(st.session_state.user_name, score, total)
            st.session_state.result_saved = True

        st.success(f"Quiz Submitted! Your final score is: {score}/{total}")
        st.balloons()

        st.subheader("Review Your Answers:")
        for i, q in enumerate(quiz_questions):
            user_ans = st.session_state.user_answers.get(i)
            correct_ans = q['answer']
            st.write(f"**Question {i+1}:** {q['question']}")
            if user_ans == correct_ans:
                st.success(f"Your answer: {user_ans} (Correct!)")
            else:
                st.error(f"Your answer: {user_ans} (Incorrect!)")
                st.info(f"Correct answer: {correct_ans}")
            st.write("---")

        if st.button("Try Again"):
            # Reset state for a new quiz
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- Leaderboard (always visible on the sidebar) ---
    st.sidebar.title("🏆 Leaderboard")
    results = get_all_results()
    if results:
        df = pd.DataFrame(results, columns=['Name', 'Score', 'Total', 'Timestamp'])
        df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%d %H:%M')
        st.sidebar.dataframe(df, hide_index=True)
    else:
        st.sidebar.write("No results yet. Be the first!")

if __name__ == "__main__":
    main()
