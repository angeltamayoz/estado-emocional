from flask import Blueprint, request, jsonify
from .utils import read_csv, write_csv

routes = Blueprint('routes', __name__)

CSV_FILE_PATH = 'data.csv'

# Example route to read data from CSV
@routes.route('/data', methods=['GET'])
def get_data():
    try:
        data = read_csv(CSV_FILE_PATH)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found."}), 404

# Example route to write data to CSV
@routes.route('/data', methods=['POST'])
def add_data():
    try:
        new_data = request.json
        fieldnames = new_data.keys()
        existing_data = []
        try:
            existing_data = read_csv(CSV_FILE_PATH)
        except FileNotFoundError:
            pass
        existing_data.append(new_data)
        write_csv(CSV_FILE_PATH, existing_data, fieldnames)
        return jsonify({"message": "Data added successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500