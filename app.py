from flask import Flask, jsonify, request, send_from_directory
import pandas as pd
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the blood bank data (ensure correct file path)
blood_bank_data = pd.read_csv("blood_bank.csv")  # Path to uploaded CSV

# Strip extra spaces from column names to avoid issues
blood_bank_data.columns = blood_bank_data.columns.str.strip()

# Handle NaN values (replace NaN with empty string or some other value)
blood_bank_data = blood_bank_data.fillna("")  # Replaces NaN with empty string

# Print the column names to debug
print("CSV Columns:", blood_bank_data.columns)

# Function to get the list of all states
def get_states():
    return blood_bank_data['State'].unique().tolist()  # Get unique states from 'State' column

# Function to get the list of districts for a specific state
def get_districts(state):
    state = state.lower()  # Normalize to lowercase for comparison
    return blood_bank_data[blood_bank_data['State'].str.lower() == state]['District'].unique().tolist()

# API to get list of all states
@app.route('/api/states', methods=['GET'])
def api_get_states():
    states = get_states()  # Get unique states
    return jsonify(states)

# API to get districts based on selected state
@app.route('/api/districts', methods=['GET'])
def api_get_districts():
    state = request.args.get('state', default=None, type=str)
    if state:
        districts = get_districts(state)
        return jsonify(districts)
    return jsonify({"error": "State parameter is required"}), 400

# API to get filtered blood bank data based on state and district
@app.route('/api/blood-bank-data', methods=['GET'])
def api_get_blood_bank_data():
    state = request.args.get('state', default=None, type=str)
    district = request.args.get('district', default=None, type=str)
    
    if not state:
        return jsonify({"error": "State parameter is required"}), 400
    
    filtered_data = blood_bank_data
    
    # Apply filters based on state and district (no blood type filtering anymore)
    if state:
        filtered_data = filtered_data[filtered_data['State'].str.lower() == state.lower()]
    if district:
        filtered_data = filtered_data[filtered_data['District'].str.lower() == district.lower()]

    # Return filtered data as JSON
    return jsonify(filtered_data.to_dict(orient='records'))  # Return filtered data as JSON

# Route to serve the blood.html file directly from static folder
@app.route('/')
def blood():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'blood.html')

if __name__ == '__main__':
    app.run(debug=True)
