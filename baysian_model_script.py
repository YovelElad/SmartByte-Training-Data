import pandas as pd
import numpy as np
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork


class BaysianModel:
    def __init__(self):
        self.data = pd.read_csv("mock_data.csv")
        self.discretize_data()
        self.model = self.create_bayesian_network()
        self.fit_model()

    """
    discretize() : function that discretizes the specified column in the data.
    """

    def discretize(self, column, bins, labels):
        self.data[column] = pd.cut(self.data[column], bins=bins, labels=labels)

    def discretize_data(self):
        self.discretize('temperature', bins=[-np.inf, 15, 20, 27, np.inf], labels=[1, 2, 3, 4])
        self.discretize('humidity', bins=[-np.inf, 30, 60, 90, np.inf], labels=[1, 2, 3, 4])
        self.discretize('distance_from_house', bins=[-np.inf, 0.01, 20, np.inf], labels=[1, 2, 3])

        self.data['hour'] = self.data['timestamp'].apply(lambda x: int(x.split()[1].split(':')[0]))
        self.discretize('hour', bins=[-np.inf, 12, 18, np.inf], labels=[1, 2, 3])

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

    def fit_model(self):
        # BDeu-Bayesian Dirichlet equivalent uniformwhat
        """
         Returns the DiscreteFactor object, which can be printed to show the probability distribution of the device's state.
         it uses the Bayesian Network model to compute the probability distribution of the device's state, given the evidence.
         This information can be used to make recommendations about how to control the device in the smart home system.
        """
        self.data = pd.read_csv("mock_data.csv")
        self.model.fit(self.data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)

    def recommend_device(self, devices, evidence):
        threshold = 0.5
        result_array = []
        for device in devices:
            inference = VariableElimination(self.model)
            result = inference.query(variables=[device], evidence=evidence)
            probabilities = dict(zip(["off", "on"], result.values.tolist()))
            recommendation = "on" if probabilities["on"] > threshold else "off"
            result_dict = {
                'variables': result.variables,
                'cardinality': result.cardinality.tolist(),
                'probabilities': probabilities,
                'recommendation': recommendation
            }
            result_array.append(result_dict)
        return result_array
