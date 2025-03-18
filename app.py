from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

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

@app.route('/bundle-analysis', methods=['POST'])
def bundle_analysis():
    data = request.json
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
            data = bundle_data[bundle]
            response_data["tableData"].append({
                "bundle": bundle.replace("bundle", "Bundle "),
                "sales": data["sales"],
                "marketShare": data["marketShare"],
                "profit": data["profit"]
            })
            response_data["chartLabels"].append(bundle.replace("bundle", "Bundle "))
            response_data["salesData"].append(data["sales"])
            response_data["marketShareData"].append(data["marketShare"])

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)