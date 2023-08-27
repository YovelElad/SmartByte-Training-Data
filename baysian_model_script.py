import pandas as pd
import numpy as np
import requests
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork
from sensors import SensorFactory
from devices_manager import Manager
from constants import (DEVICE_THRESHOLD_URL,
                       MIN_EVIDENCE_STRENGTH_THRESHOLD,
                       DEFAULT_DEVICE_THRESHOLD,
                       DEFAULT_AVERAGE_DURATION, SensorTypes)

class BaysianModel:
    def __init__(self, file_name, logger):
        self.data = pd.read_csv(file_name)
        self.logger = logger
        self.initialize_sensors()
        self.discretize_data()
        self.model = self.create_bayesian_network()
        self.fit_model()

    def get_most_recent_values(self):
        latest_data = self.data.iloc[-1]
        return {
            'temperature': latest_data['temperature'],
            'humidity': latest_data['humidity'],
            'season': latest_data['season']
        }

    def initialize_sensors(self):
        self.sensors = {}
        sensor_list = Manager.get_list_of_sensor_values()
        for sensor_name in sensor_list:
            if sensor_name != "hour":  # Exclude the 'hour' column
                self.sensors[sensor_name] = SensorFactory.create_sensor(sensor_name)

    def get_device_thresholds(self):
        response = requests.get(DEVICE_THRESHOLD_URL)
        if response.status_code == 200:
            return {device["device_id"]: device["threshold"] for device in response.json()}
        else:
            raise Exception("Unable to fetch device thresholds")

    def read_data(self, file_name):
        self.data = pd.read_csv(file_name)

    def update_data(self, new_data):
        self.logger.append_data_to_csv(new_data)

    """
    discretize() : function that discretizes the specified column in the data.
    """

    def discretize(self, column, bins, labels):
        self.data[column] = pd.cut(self.data[column], bins=bins, labels=labels)

    def discretize_data(self):
        for sensor_name, sensor_obj in self.sensors.items():
            if sensor_obj.bins() is not None:
                self.discretize(sensor_obj.name(), bins=sensor_obj.bins(), labels=sensor_obj.labels())
            else:
                # This is where we can use our new method for the season.
                if sensor_name == SensorTypes.SEASON.value:
                    self.data['season'] = self.data['season'].apply(sensor_obj.transform_to_integer)
                else:
                    print(f"Error: Sensor {sensor_obj.name()} has no bins defined!")

        # Handle 'hour' column
        self.data['hour'] = self.data['timestamp'].apply(lambda x: int(x.split()[1].split(':')[0]))
        self.discretize('hour', bins=[-np.inf, 12, 18, np.inf], labels=[1, 2, 3])

        # Drop the 'timestamp' column
        self.data.drop(columns=['timestamp'], inplace=True)



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

        if 'distance' in evidence:
            if evidence['distance'] <= 0.01:
                evidence['distance'] = 1
            elif evidence['distance'] <= 20:
                evidence['distance'] = 2
            else:
                evidence['distance'] = 3

        if 'hour' in evidence:
            if evidence['hour'] <= 12:
                evidence['hour'] = 1
            elif evidence['hour'] <= 18:
                evidence['hour'] = 2
            else:
                evidence['hour'] = 3

        return evidence

    def recommend_device(self, devices, evidence):
        # Fetch the most recent values if not provided in evidence
        if 'temperature' not in evidence:
            evidence['temperature'] = self.get_most_recent_values()['temperature']
        if 'humidity' not in evidence:
            evidence['humidity'] = self.get_most_recent_values()['humidity']
        if 'season' not in evidence:
            evidence['season'] = self.get_most_recent_values()['season']
        device_thresholds = self.get_device_thresholds()
        average_strength, individual_strengths = self.calculate_average_connection_strength(devices, evidence)
        result_array = []
        for device in devices:
            base_threshold = device_thresholds.get(device, DEFAULT_DEVICE_THRESHOLD)
            threshold = base_threshold + (1 - base_threshold) * (individual_strengths[device] - average_strength) - 0.1
            inference = VariableElimination(self.model)
            result = inference.query(variables=[device], evidence=evidence)
            probabilities = dict(zip(["off", "on"], result.values.tolist()))
            recommendation = "on" if probabilities["on"] > threshold else "off"
            correlation = individual_strengths[device]
            strongest_evidence = {}
            for ev_key, ev_val in evidence.items():
                updated_evidence = {k: v for k, v in evidence.items() if k != ev_key}
                updated_strength, _ = self.calculate_average_connection_strength([device], updated_evidence)
                influence = abs(individual_strengths[device] - updated_strength)
                strongest_evidence[ev_key] = influence
            filtered_strongest_evidence = {k: v for k, v in strongest_evidence.items() if
                                           v >= MIN_EVIDENCE_STRENGTH_THRESHOLD}
            sorted_evidence = sorted(filtered_strongest_evidence.items(), key=lambda x: x[1], reverse=True)
            formatted_strongest_evidence = [{'evidence': item[0], 'value': item[1]} for item in sorted_evidence]
            device_duration_column = dict(zip(Manager.get_list_of_devices(),
                                              Manager.get_list_of_devices_with_duration_postfix()))
            matching_rows = self.data[self.data[device] == "on"]
            if not matching_rows.empty:
                average_duration = matching_rows[device_duration_column[device]].mean()
            else:
                average_duration = DEFAULT_AVERAGE_DURATION
            result_dict = {
                'device': device,
                'variables': result.variables,
                'cardinality': result.cardinality.tolist(),
                'probabilities': probabilities,
                'recommendation': recommendation,
                'strongest_evidence': formatted_strongest_evidence,
                'correlation': correlation,
                'average_duration': average_duration
            }
            result_array.append(result_dict)
        return result_array
