from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd

app = Flask(__name__)

# Allow frontend access from Netlify
CORS(app, resources={r"/*": {"origins": "https://conjoint-manager-demo.netlify.app"}}, supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Path to preloaded data file
DATA_FILE = "data/bundling_data.csv"

# Load data when the server starts
if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE) if DATA_FILE.endswith('.csv') else pd.read_excel(DATA_FILE)

        # Perform initial processing (aggregate sales, market share, profit margin)
        grouped_data = df.groupby('Bundle').agg({
            'Sales': 'sum',
            'Market Share': 'mean',
            'Profit Margin': 'mean'
        }).reset_index()

    except Exception as e:
        print(f"Error loading data file: {e}")
        df = None
        grouped_data = None
else:
    print(f"⚠️ Data file not found at {DATA_FILE}")
    df = None
    grouped_data = None

@app.route('/get-analysis', methods=['GET'])
def get_analysis():
    # Returns processed data for frontend visualization
    if grouped_data is None:
        return jsonify({'error': 'Data file not loaded'}), 500

    response_data = {
        "tableData": grouped_data.to_dict(orient="records"),
        "chartLabels": grouped_data["Bundle"].tolist(),
        "salesData": grouped_data["Sales"].tolist(),
        "marketShareData": grouped_data["Market Share"].tolist(),
        "profitData": grouped_data["Profit Margin"].tolist()
    }

    return jsonify(response_data)

@app.route('/setup', methods=['POST'])
def receive_setup():
    # Receives and stores product setup information
    product_setup = request.json
    print("Received product setup:", product_setup)
    return jsonify({"message": "Product setup saved successfully!"})

@app.route('/bundle-analysis', methods=['POST'])
def bundle_analysis():
    # Analyzes selected bundles and returns relevant data
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400

        selected_bundles = data.get("bundles", [])
        chart_type = data.get("chartType", "bar")

        if grouped_data is None:
            return jsonify({'error': 'Data file not loaded'}), 500

        # Filter only selected bundles
        filtered_data = grouped_data[grouped_data["Bundle"].isin(selected_bundles)]

        response_data = {
            "tableData": filtered_data.to_dict(orient="records"),
            "chartLabels": filtered_data["Bundle"].tolist(),
            "salesData": filtered_data["Sales"].tolist(),
            "marketShareData": filtered_data["Market Share"].tolist(),
            "profitData": filtered_data["Profit Margin"].tolist()
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def add_cors_headers(response):
    # Ensures all responses include CORS headers
    response.headers["Access-Control-Allow-Origin"] = "https://conjoint-manager-demo.netlify.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

if __name__ == '__main__':
    app.run(debug=True)
    