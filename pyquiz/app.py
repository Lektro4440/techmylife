from flask import Flask, render_template, request, redirect, url_for, session
import requests
import random
import sqlite3

app = Flask(__name__)
app.secret_key = 'the_most_epic_secret_key_ever'

# Initialize the database or connect to an existing one
def initialize_database():
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Fetch leaderboard data from the database
def get_leaderboard():
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, score FROM leaderboard ORDER BY score DESC')
    leaderboard_data = cursor.fetchall()
    conn.close()
    return leaderboard_data

categories = ["General Knowledge", "Books", "Film", "Music", "Musicals & Theatres", "Television", "Video Games"]
difficulties = ["easy", "medium", "hard"]

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        category = request.form.get('category')
        difficulty = request.form.get('difficulty')

        if username:
            session['username'] = username
            session['score'] = 0
            session['category'] = category
            session['difficulty'] = difficulty
            session['questions'] = []  # Initialize questions list
            return redirect(url_for('quiz'))
        else:
            return "Please enter a username to start the quiz.", 400

    return render_template('index.html', categories=categories, difficulties=difficulties)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = session.get('correct_answer', '')

        if user_answer == correct_answer:
            session['score'] += 1

        # Remove the current question from the list
        if session['questions']:
            session['questions'].pop(0)

        # Check if there are more questions
        if session['questions']:
            return redirect(url_for('quiz'))
        else:
            return redirect(url_for('end_quiz'))
    else:
        category = session.get('category', '').replace(" ", "%20").lower()
        difficulty = session.get('difficulty', '')

        api_url = f"https://the-trivia-api.com/api/questions?limit=5&categories={category}&difficulty={difficulty}"
        response = requests.get(api_url)

        if response.status_code == 200:
            question_data = response.json()
            session['questions'] = question_data

            # Check if "options" field is present in the question data
            current_question = question_data[0]
            if "options" in current_question:
                session['correct_answer'] = current_question["correctAnswer"]
                options = current_question.get("options", [])
                random.shuffle(options)
                return render_template('quiz.html', question=current_question, options=options, score=session.get('score', 0))
            else:
                # Handle case where "options" are missing
                return "Error: 'options' field is missing in question data", 500
        else:
            return "Error fetching questions from The Trivia API", 500


@app.route('/end_quiz')
def end_quiz():
    # Update the leaderboard with the user's score
    username = session.get('username', 'Anonymous')
    score = session.get('score', 0)
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leaderboard (username, score) VALUES (?, ?)", (username, score))
    conn.commit()
    conn.close()

    return redirect(url_for('leaderboard'))

@app.route('/leaderboard')
def leaderboard():
    # Initialize the database (only needs to be done once)
    initialize_database()

    # Fetch the leaderboard data
    leaderboard_data = get_leaderboard()

    # Create a list of dictionaries for each user's data
    leaderboard = [{'username': row[0], 'score': row[1]} for row in leaderboard_data]

    return render_template('leaderboard.html', leaderboard=leaderboard)

if __name__ == '__main__':
    app.run(debug=True)
