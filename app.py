from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Allow frontend access from Netlify
CORS(app, resources={r"/*": {"origins": "https://conjoint-manager-demo.netlify.app"}}, supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

product_setup = {}

@app.route('/setup', methods=['POST'])
def receive_setup():
    global product_setup
    product_setup = request.json
    print("Received product setup:", product_setup)
    return jsonify({"message": "Product setup saved successfully!"})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    return jsonify({'message': f'File {file.filename} uploaded successfully!', 'filepath': filepath})

@app.route('/bundle-analysis', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'message': 'CORS preflight successful'})
    response.headers.add("Access-Control-Allow-Origin", "https://conjoint-manager-demo.netlify.app")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response

@app.route('/bundle-analysis', methods=['POST'])
def bundle_analysis():
    try:
        print("Received request for /bundle-analysis")
        print("Raw Request Data:", request.data.decode('utf-8'))
        print("Request Headers:", dict(request.headers))

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON format or missing Content-Type header"}), 400

        selected_bundles = data.get("bundles", [])
        chart_type = data.get("chartType", "bar")

        # Simulated performance data for each bundle
        bundle_data = {
            "bundle1": {"sales": 20000, "marketShare": 15, "profit": 30},
            "bundle2": {"sales": 25000, "marketShare": 20, "profit": 35},
            "bundle3": {"sales": 18000, "marketShare": 12, "profit": 40},
        }

        response_data = {
            "tableData": [],
            "chartLabels": [],
            "salesData": [],
            "marketShareData": []
        }

        for bundle in selected_bundles:
            if bundle in bundle_data:
                bundle_info = bundle_data[bundle]
                response_data["tableData"].append({
                    "bundle": bundle.replace("bundle", "Bundle "),
                    "sales": bundle_info["sales"],
                    "marketShare": bundle_info["marketShare"],
                    "profit": bundle_info["profit"]
                })
                response_data["chartLabels"].append(bundle.replace("bundle", "Bundle "))
                response_data["salesData"].append(bundle_info["sales"])
                response_data["marketShareData"].append(bundle_info["marketShare"])

        print("Response Data:", response_data)
        return jsonify(response_data)

    except Exception as e:
        print("Error processing /bundle-analysis:", str(e))
        return jsonify({"error": str(e)}), 500

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "https://conjoint-manager-demo.netlify.app"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

if __name__ == '__main__':
    app.run(debug=True)