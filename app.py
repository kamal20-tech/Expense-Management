from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from utils.ocr import extract_and_classify_expense

# Flask App Setup
app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
DB_PATH = 'database/expenses.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (id INTEGER PRIMARY KEY, income REAL, debt REAL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY, amount REAL, category TEXT, description TEXT, date TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch income and debt
    cursor.execute('SELECT income, debt FROM user_data LIMIT 1')
    user_data = cursor.fetchone()

    # Fetch expenses
    cursor.execute('SELECT * FROM expenses')
    expenses = cursor.fetchall()

    conn.close()

    total_expenses = sum(expense[1] for expense in expenses)
    income = user_data[0] if user_data else 0
    debt = user_data[1] if user_data else 0

    financial_health_score = max(0, 100 - ((debt / income) * 100)) if income > 0 else 0

    return render_template('index.html', income=income, debt=debt, expenses=expenses, total_expenses=total_expenses, financial_health_score=financial_health_score)

@app.route('/set_income', methods=['POST'])
def set_income():
    income = float(request.form['income'])
    debt = float(request.form['debt'])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_data')
    cursor.execute('INSERT INTO user_data (income, debt) VALUES (?, ?)', (income, debt))
    conn.commit()
    conn.close()

    flash('Income and debt saved successfully!')
    return redirect(url_for('index'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    amount = float(request.form['amount'])
    category = request.form['category']
    description = request.form['description']
    date = request.form['date']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)', (amount, category, description, date))
    conn.commit()
    conn.close()

    flash('Expense added successfully!')
    return redirect(url_for('index'))

@app.route('/upload_receipt', methods=['POST'])
def upload_receipt():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    extracted_text, predicted_category = extract_and_classify_expense(file_path)
    flash(f'Extracted Text: {extracted_text}')
    flash(f'Predicted Category: {predicted_category}')

    os.remove(file_path)  # Clean up after processing
    return redirect(url_for('index'))

@app.route('/reset_data', methods=['POST'])
def reset_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_data')
    cursor.execute('DELETE FROM expenses')
    conn.commit()
    conn.close()

    flash('All data has been reset!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
