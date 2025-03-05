from flask import Flask, request, jsonify
from flask_cors import CORS  # NEW

app = Flask(__name__)
CORS(app)  # NEW - allows cross-origin requests from anywhere (or restrict to specific domains)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    product_name = data['productName']
    attributes = data['attributes']

    analysis_result = {
        "product": product_name,
        "total_attributes": len(attributes),
        "example_attribute": attributes[0] if attributes else None
    }

    return jsonify({
        "message": f"Received {len(attributes)} attributes for {product_name}",
        "analysis": analysis_result
    })

if __name__ == '__main__':
    app.run(debug=True)
