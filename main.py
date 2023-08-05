import numpy as np
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS

from baysian_model_script import BaysianModel
from logger import Logger

app = Flask(__name__)
CORS(app)
baysian_model = BaysianModel("mock_data.csv", Logger("mock_data.csv"))

MIN_CORRELATION_THRESHOLD = 0.3


@app.route('/recommend_device', methods=['POST'])
def recommend_device_api():
    data = request.get_json()
    device = data['devices']
    evidence = data['evidence']

    print("Evidence:", evidence)  # Debug the content of the evidence variable

    result = baysian_model.recommend_device(device, evidence)

    # Filter the suggestions based on the minimum correlation threshold
    filtered_result = [device for device in result if device['correlation'] >= MIN_CORRELATION_THRESHOLD]

    return jsonify(filtered_result)

@app.route('/update_data', methods=['POST'])
def update_data_api():
    data = request.get_json()
    logger = Logger(baysian_model.data)
    logger.append_data_to_csv(data)
    baysian_model.data = pd.read_csv(baysian_model.data)  # Read the updated data
    baysian_model.discretize_data()  # Discretize the updated data
    baysian_model.fit_model()
    return jsonify({"status": "success", "message": "Data updated successfully"})


def calculate_total_energy(df, devices):
    total_energy = np.zeros(len(df))
    for device in devices:
        total_energy += df[device].sum()

    return total_energy.tolist()


@app.route('/graph-data', methods=['GET'])
def get_graph_data():
    device = request.args.get('device', 'ac_energy')
    time_range = request.args.get('time_range', 'daily')
    year = request.args.get('year')
    if not device:
        device = 'ac_energy'
    df = pd.read_csv('mock_data.csv')

    if time_range == 'daily':
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.date)
    elif time_range == 'monthly':
        if year:
            df = df[pd.to_datetime(df['timestamp']).dt.year == int(year)]
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.to_period('M'))
    elif time_range == 'yearly':
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.to_period('Y'))
    else:
        df_grouped = df.groupby(pd.to_datetime(df['timestamp']).dt.date)

    labels = df_grouped.indices.keys()

    # Convert Period objects to string format for monthly and yearly time ranges
    if time_range == 'monthly':
        labels = [label.strftime("%Y-%m") for label in labels]
    elif time_range == 'yearly':
        labels = [label.strftime("%Y") for label in labels]

    # Calculate total energy consumption for the selected device
    data = calculate_total_energy(df_grouped, [device])

    return jsonify({'labels': labels, 'data': data})


if __name__ == '__main__':
    app.run()
