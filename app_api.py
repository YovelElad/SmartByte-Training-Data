from flask import Flask, request, jsonify
import baysian_model_script

app = Flask(__name__)


@app.route('/recommend_device', methods=['POST'])
def recommend_device_api():
    data = request.get_json()
    device = data.get('device')
    evidence = data.get('evidence')

    result = baysian_model_script.recommend_device(device, evidence)
    return jsonify(result)


if __name__ == '__main__':
    app.run()
