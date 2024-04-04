from flask import Flask, render_template, request, jsonify
import joblib

app = Flask(__name__)

# Load the saved model
model = joblib.load('model/random_forest_model.joblib')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.form.to_dict()
    input_data = [[float(data['Density']), int(data['Age']), float(data['Weight']),
                   float(data['Height']), float(data['Neck']), float(data['Chest']), float(data['Abdomen']),
                   float(data['Hip']), float(data['Thigh']), float(data['Knee']), float(data['Ankle']),
                   float(data['Biceps']), float(data['Forearm']), float(data['Wrist'])]]
    prediction = model.predict(input_data)[0]
    return jsonify({'prediction': prediction})

if __name__ == '__main__':
    app.run(debug=True)