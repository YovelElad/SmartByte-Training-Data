import pandas as pd
import numpy as np
import requests
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork

from sensors import TemperatureSensor, HumiditySensor, DistanceSensor, Manager, SoilSensor

MIN_EVIDENCE_STRENGTH_THRESHOLD = 0.001


def get_device_thresholds():
    url = "http://localhost:3001/devices_with_thresholds"
    response = requests.get(url)
    if response.status_code == 200:
        return {device["device_id"]: device["threshold"] for device in response.json()}
    else:
        raise Exception("Unable to fetch device thresholds")


class BaysianModel:
    def __init__(self, file_name):
        self.data = pd.read_csv(file_name)
        self.discretize_data()
        self.model = self.create_bayesian_network()
        self.fit_model()

    """
    discretize() : function that discretizes the specified column in the data.
    """

    def read_data(self, file_name):
        self.data = pd.read_csv(file_name)

    def discretize(self, column, bins, labels):
        self.data[column] = pd.cut(self.data[column], bins=bins, labels=labels)

    def discretize_data(self):
        self.discretize(TemperatureSensor.name(), bins=TemperatureSensor.bins(),
                        labels=TemperatureSensor.labels())
        self.discretize(HumiditySensor.name(), HumiditySensor.bins(), HumiditySensor.labels())
        self.discretize(DistanceSensor.name(), DistanceSensor.bins(), DistanceSensor.labels())
        self.discretize(SoilSensor.name(), SoilSensor.bins(), SoilSensor.labels())

        self.data['hour'] = self.data['timestamp'].apply(lambda x: int(x.split()[1].split(':')[0]))
        self.discretize('hour', bins=[-np.inf, 12, 18, np.inf], labels=[1, 2, 3])

        # Drop the 'timestamp' column
        self.data.drop(columns=['timestamp'], inplace=True)

        # Replace season string values with integer labels
        season_mapping = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
        self.data['season'] = self.data['season'].map(season_mapping)

    def create_bayesian_network(self):
        """
        Create a Bayesian Network model by specifying the relationships between variables as a list of tuples.
        Each tuple represents an edge in the network, with the first element being the parent node and the second element being the child node.
        """
        device_sensor_connections = []

        for device in Manager.get_list_of_devices():
            device_sensor_connections.extend([(sensor, device) for sensor in Manager.get_list_of_sensor_values()])

        return BayesianNetwork(device_sensor_connections)

    def calculate_average_connection_strength(self, devices, evidence):
        inference = VariableElimination(self.model)
        connection_strengths = []

        for device in devices:
            result = inference.query(variables=[device], evidence=evidence)
            connection_strength = result.values[1]  # Probability of strong connection
            connection_strengths.append(connection_strength)

        average_strength = sum(connection_strengths) / len(connection_strengths)
        individual_strengths = dict(zip(devices, connection_strengths))

        return average_strength, individual_strengths

    def fit_model(self):
        # BDeu-Bayesian Dirichlet equivalent uniformwhat
        """
         Returns the DiscreteFactor object, which can be printed to show the probability distribution of the device's state.
         it uses the Bayesian Network model to compute the probability distribution of the device's state, given the evidence.
         This information can be used to make recommendations about how to control the device in the smart home system.
        """
        self.model.fit(self.data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)

    def discretize_evidence(self, evidence):
        if 'temperature' in evidence:
            if evidence['temperature'] <= 15:
                evidence['temperature'] = 1
            elif evidence['temperature'] <= 20:
                evidence['temperature'] = 2
            elif evidence['temperature'] <= 25:
                evidence['temperature'] = 3
            elif evidence['temperature'] <= 32:
                evidence['temperature'] = 4
            else:
                evidence['temperature'] = 5

        if 'humidity' in evidence:
            if evidence['humidity'] <= 30:
                evidence['humidity'] = 1
            elif evidence['humidity'] <= 60:
                evidence['humidity'] = 2
            elif evidence['humidity'] <= 90:
                evidence['humidity'] = 3
            else:
                evidence['humidity'] = 4

        if 'distance_from_house' in evidence:
            if evidence['distance_from_house'] <= 0.01:
                evidence['distance_from_house'] = 1
            elif evidence['distance_from_house'] <= 20:
                evidence['distance_from_house'] = 2
            else:
                evidence['distance_from_house'] = 3

        if 'hour' in evidence:
            if evidence['hour'] <= 12:
                evidence['hour'] = 1
            elif evidence['hour'] <= 18:
                evidence['hour'] = 2
            else:
                evidence['hour'] = 3

        return evidence



    def recommend_device(self, devices, evidence):
        device_thresholds = get_device_thresholds()
        average_strength, individual_strengths = self.calculate_average_connection_strength(devices, evidence)
        result_array = []

        for device in devices:
            base_threshold = device_thresholds.get(device, 0.6)
            threshold = base_threshold + (1 - base_threshold) * (individual_strengths[device] - average_strength)-0.1
            inference = VariableElimination(self.model)
            result = inference.query(variables=[device], evidence=evidence)
            probabilities = dict(zip(["off", "on"], result.values.tolist()))
            recommendation = "on" if probabilities["on"] > threshold else "off"
            correlation = individual_strengths[device]

            # Find the most influential evidence for the device
            strongest_evidence = {}
            for ev_key, ev_val in evidence.items():
                updated_evidence = {k: v for k, v in evidence.items() if k != ev_key}
                updated_strength, _ = self.calculate_average_connection_strength([device], updated_evidence)
                influence = abs(individual_strengths[device] - updated_strength)
                strongest_evidence[ev_key] = influence

            # Filter the strongest evidence based on the minimum evidence strength threshold
            filtered_strongest_evidence = {k: v for k, v in strongest_evidence.items() if
                                           v >= MIN_EVIDENCE_STRENGTH_THRESHOLD}
            sorted_evidence = sorted(filtered_strongest_evidence.items(), key=lambda x: x[1], reverse=True)
            formatted_strongest_evidence = [{'evidence': item[0], 'value': item[1]} for item in sorted_evidence]

            device_duration_column = {
                'ac_status': 'ac_duration',
                'fan': 'fan_duration',
                'heater_switch': 'heater_duration',
                'lights': 'lights_duration',
                'laundry_machine': 'laundry_duration',
                'pump': 'pump_duration'
            }
            mapped_evidence=self.discretize_evidence(evidence.copy())
            # Select rows where the device is "on"
            matching_rows = self.data[self.data[device] == "on"]
            # Calculate the average duration for this device
            if not matching_rows.empty:
                average_duration = matching_rows[device_duration_column[device]].mean()
            else:
                average_duration = 1  # or a suitable default value


            result_dict = {
                'device': device,
                'variables': result.variables,
                'cardinality': result.cardinality.tolist(),
                'probabilities': probabilities,
                'recommendation': recommendation,
                'strongest_evidence': formatted_strongest_evidence,
                'correlation': correlation,
                'average_duration': average_duration  # Add the average duration to the result
            }


            result_array.append(result_dict)

        return result_array
