from flask import Flask, request, jsonify
import baysian_model_script
from generate_dataset import append_data_to_csv

app = Flask(__name__)


@app.route('/recommend_device', methods=['POST'])
def recommend_device_api():
    data = request.get_json()
    device = data['devices']
    evidence = data['evidence']
    result = baysian_model_script.recommend_device(device, evidence)
    return jsonify(result)


@app.route('/update_data', methods=['POST'])
def update_data_api():
    data = request.get_json()
    append_data_to_csv(data, "mock_data.csv")
    return jsonify({"status": "success", "message": "Data updated successfully"})




if __name__ == '__main__':
    app.run()
