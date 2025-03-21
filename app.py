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

conjoint_file = "data/credit_card_parameters.csv"

# Load data when the server starts
grouped_data = None

segments = None
conjoint_df = None

if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE) if DATA_FILE.endswith('.csv') else pd.read_excel(DATA_FILE)

        print("✅ Data file loaded successfully!")
        print(df.head())  # Debugging: Print first few rows

        # Ensure expected columns exist before aggregation
        required_columns = {'Bundle', 'Sales', 'Market Share', 'Profit Margin'}
        if not required_columns.issubset(df.columns):
            print(f"⚠️ Missing columns in dataset: {required_columns - set(df.columns)}")
            grouped_data = None
        else:
            # Perform initial processing (aggregate sales, market share, profit margin)
            grouped_data = df.groupby('Bundle', as_index=False).agg({
                'Sales': 'sum',
                'Market Share': 'mean',
                'Profit Margin': 'mean'
            })

            print("✅ Processed data for analysis:")
            print(grouped_data)

        conjoint_df = pd.read_csv(conjoint_file) if conjoint_file.endswith('.csv') else pd.read_excel(conjoint_file)
        segments = conjoint_df["Segment"].unique().tolist()

    except Exception as e:
        print(f"❌ Error loading data file: {e}")
        grouped_data = None
else:
    print(f"⚠️ Data file not found at {DATA_FILE}")

@app.route('/get-analysis', methods=['GET'])
def get_analysis():
    # Returns processed data for frontend visualization
    if grouped_data is None:
        return jsonify({'error': 'Data file not loaded or incorrect format'}), 500

    response_data = {
        "tableData": grouped_data.to_dict(orient="records"),
        "chartLabels": grouped_data["Bundle"].tolist(),
        "salesData": grouped_data["Sales"].tolist(),
        "marketShareData": grouped_data["Market Share"].tolist(),
        "profitData": grouped_data["Profit Margin"].tolist()
    }

    print("✅ Sending analysis data to frontend:")
    print(response_data)  # Debugging

    return jsonify(response_data)

@app.route('/setup', methods=['POST'])
def receive_setup():
    # Receives and stores product setup information
    product_setup = request.json
    print("Received product setup:", product_setup)
    return jsonify({"message": "Product setup saved successfully!"})

# Simulated segment data (replace with actual segmentation logic)
#customer_segments = ["Young Professionals", "Families", "Retirees", "Students", "Frequent Travelers"]

@app.route('/segments', methods=['GET'])
def get_segments():
    """Returns a list of customer segments."""
#    print("✅ Sending customer segments:", customer_segments)  # Debugging log
#    return jsonify({"segments": customer_segments})
    print("✅ Sending customer segments:", segments)  # Debugging log
    return jsonify({"segments": segments})

# Simulated feature importance data (replace with actual analysis later)
feature_importance_data = {
    "features": ["Annual Fees", "Cashback Rates", "Intro APRs", "Digital Features", "APRs", "Perks"],
    "importance": [20, 25, 15, 10, 18, 12]  # Example importance percentages
}

@app.route('/feature-importance', methods=['GET'])
def get_feature_importance():
    # Returns feature importance data for part-worth analysis
#    print("✅ Sending feature importance data:", feature_importance_data)  # Debugging log
#    return jsonify(feature_importance_data)
    try:
        selected_segment = request.args.get("segment", "All")  # Default to "All" if none provided

        result_dict = {"features": [], "importance": []}
        df_subset = conjoint_df[conjoint_df["Segment"] == selected_segment]
        df_subset = df_subset[df_subset["Attribute"] != "Segment Prob"]
        for attr, group in df_subset.groupby("Attribute"):
            max_value = group["Coefficient"].max()
            min_value = group["Coefficient"].min()
            diff = max_value - min_value

            result_dict["features"].append(attr)
            result_dict["importance"].append(diff)

        sum_diff = sum(result_dict["importance"])

        diff_pct = [d/sum_diff*100 for d in result_dict["importance"]]
        result_dict["importance"] = diff_pct

        return jsonify(result_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/segmentation-strategy', methods=['GET'])
def get_segmentation_data():
    # Sample static data for illustration
    data = [
        {
            "segment": "Value Seekers",
            "annual_fee": "$0",
            "cashback_rate": "1%",
            "intro_apr": "0% for 12 months",
            "digital_feature": "Basic App",
            "interest_rate": "20%",
            "perk": "None",
            "profit": 12000
        },
        {
            "segment": "Frequent Travelers",
            "annual_fee": "$150",
            "cashback_rate": "2%",
            "intro_apr": "0% for 18 months",
            "digital_feature": "Spend Insights",
            "interest_rate": "25%",
            "perk": "Airport Lounge",
            "profit": 27000
        },
        {
            "segment": "Premium Users",
            "annual_fee": "$500",
            "cashback_rate": "3%",
            "intro_apr": "None",
            "digital_feature": "Budget Coaching",
            "interest_rate": "30%",
            "perk": "Travel Insurance",
            "profit": 34000
        }
    ]
    return jsonify(data)

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

        print("✅ Sending filtered analysis data to frontend:")
        print(response_data)

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