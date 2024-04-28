import joblib
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import re
# Load the saved model
model = joblib.load('model/random_forest_model.joblib')

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a random string

# MySQL configurations
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bodyfat'
}

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['username'] = user['name']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Sorry Invalid email or password')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if the name is valid
        if not is_valid_name(name):
            return render_template('signup.html', error='Invalid name. Please enter a valid name.')

        # Check if email already exists
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user:
            cursor.close()
            conn.close()
            return render_template('signup.html', error='Email already exists')

        # Insert user into database
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        cursor.close()
        conn.close()

        # session['username'] = name
        return redirect(url_for('login'))
    return render_template('signup.html')

def is_valid_name(name):
    # Add your validation logic here, for example:
    # Name should contain only alphabets and spaces
    return bool(re.match("^[a-zA-Z ]+$", name))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    data = request.form.to_dict()
    input_data = [[float(data['Density']), int(data['Age']), float(data['Weight']),
                   float(data['Height']), float(data['Neck']), float(data['Chest']), float(data['Abdomen']),
                   float(data['Hip']), float(data['Thigh']), float(data['Knee']), float(data['Ankle']),
                   float(data['Biceps']), float(data['Forearm']), float(data['Wrist'])]]
    prediction = model.predict(input_data)[0]
    return jsonify({'prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)
