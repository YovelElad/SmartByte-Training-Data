from flask import Flask, request, jsonify
import baysian_model_script
from generate_dataset import append_data_to_csv
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


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

@app.route('/devices', methods=['GET'])
def get_devices():
    devices = [
        {"device": "ac_energy", "name": "AC"},
        {"device": "heater_energy", "name": "Heater"},
        {"device": "laundry_energy", "name": "Laundry Machine"},
    ]
    return jsonify(devices)



@app.route('/graph-data', methods=['GET'])
def get_graph_data():
    device = request.args.get('device', 'ac_energy')
    time_range = request.args.get('time_range', 'daily')
    df = pd.read_csv('mock_data.csv')
    if time_range == 'daily':
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.date)[device].sum()
    elif time_range == 'monthly':
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.to_period('M'))[device].sum()
    elif time_range == 'yearly':
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.to_period('Y'))[device].sum()
    else:
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.date)[device].sum()

    labels = df_grouped.index.tolist()

    # Convert Period objects to string format for monthly and yearly time ranges
    if time_range == 'monthly':
        labels = [label.strftime("%Y-%m") for label in labels]
    elif time_range == 'yearly':
        labels = [label.strftime("%Y") for label in labels]

    data = df_grouped.values.tolist()

    return jsonify({'labels': labels, 'data': data})


if __name__ == '__main__':
    app.run()
