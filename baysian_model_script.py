import pandas as pd
import numpy as np
import requests
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork

def get_device_thresholds():
    url = "http://localhost:3001/devices_with_thresholds"
    response = requests.get(url)
    if response.status_code == 200:
        return {device["device_id"]: device["threshold"] for device in response.json()}
    else:
        raise Exception("Unable to fetch device thresholds")


class BaysianModel:
    def __init__(self):
        self.data = pd.read_csv("mock_data.csv")
        self.discretize_data()
        self.model = self.create_bayesian_network()
        self.fit_model()

    """
    discretize() : function that discretizes the specified column in the data.
    """

    def read_data(self):
        self.data= pd.read_csv("mock_data.csv")

    def discretize(self, column, bins, labels):
        self.data[column] = pd.cut(self.data[column], bins=bins, labels=labels)

    def discretize_data(self):
        self.discretize('temperature', bins=[-np.inf, 15, 20, 27, np.inf], labels=[1, 2, 3, 4])
        self.discretize('humidity', bins=[-np.inf, 30, 60, 90, np.inf], labels=[1, 2, 3, 4])
        self.discretize('distance_from_house', bins=[-np.inf, 0.01, 20, np.inf], labels=[1, 2, 3])

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
        return BayesianNetwork([('season', 'temperature'),
                                ('hour', 'lights'),
                                ('hour', 'fan'),
                                ('temperature', 'fan'),
                                ('hour', 'heater_switch'),
                                ('temperature', 'heater_switch'),
                                ('temperature', 'ac_status'),
                                ('humidity', 'ac_status'),
                                ('season', "ac_status"),
                                ('distance_from_house', 'laundry_machine')])

    def calculate_average_connection_strength(self, devices, evidence):
        total_strength = 0
        total_connections = 0
        print("Evidence:", evidence)  # Add this line to print the evidence

        for device in devices:
            inference = VariableElimination(self.model)
            result = inference.query(variables=[device], evidence=evidence)
            probabilities = dict(zip(["off", "on"], result.values.tolist()))
            total_strength += probabilities["on"]
            total_connections += 1

        if total_connections > 0:
            return total_strength / total_connections
        else:
            return 0


    def fit_model(self):
        # BDeu-Bayesian Dirichlet equivalent uniformwhat
        """
         Returns the DiscreteFactor object, which can be printed to show the probability distribution of the device's state.
         it uses the Bayesian Network model to compute the probability distribution of the device's state, given the evidence.
         This information can be used to make recommendations about how to control the device in the smart home system.
        """
        #self.read_data()
        self.model.fit(self.data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)

    def recommend_device(self, devices, evidence):
        device_thresholds = get_device_thresholds()
        print(device_thresholds)
        average_strength = self.calculate_average_connection_strength(devices, evidence)
        print(average_strength)
        result_array = []
        print(evidence)
        for device in devices:
            base_threshold = device_thresholds.get(device, 0.6)
            threshold = base_threshold + average_strength * (1 - base_threshold)
            inference = VariableElimination(self.model)
            result = inference.query(variables=[device], evidence=evidence)
            probabilities = dict(zip(["off", "on"], result.values.tolist()))
            recommendation = "on" if probabilities["on"] > threshold else "off"
            result_dict = {
                'device': device,
                'variables': result.variables,
                'cardinality': result.cardinality.tolist(),
                'probabilities': probabilities,
                'recommendation': recommendation
            }
            result_array.append(result_dict)

        return result_array


