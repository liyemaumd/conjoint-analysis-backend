from flask import Flask, request, jsonify

app = Flask(__name__)

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