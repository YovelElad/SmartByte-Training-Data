import pandas as pd
import numpy as np
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.inference import VariableElimination
from pgmpy.models import BayesianNetwork

"""
Read the data from a CSV file named mock_data.csv using pandas.

"""
data = pd.read_csv("mock_data.csv")


def discretize_data(column, bins, labels):
    return pd.cut(column, bins=bins, labels=labels)


"""
discretize() : function that discretizes the specified column in the data.
"""


def discretize(column, bins, labels):
    data[column] = pd.cut(data[column], bins=bins, labels=labels)


discretize('temperature', bins=[-np.inf, 15, 20, 27, np.inf], labels=[1, 2, 3, 4])
discretize('humidity', bins=[-np.inf, 30, 60, 90, np.inf], labels=[1, 2, 3, 4])
discretize('distance_from_house', bins=[-np.inf, 0.01, 20, np.inf], labels=[1, 2, 3])

data['hour'] = data['timestamp'].apply(lambda x: int(x.split()[1].split(':')[0]))
discretize('hour', bins=[-np.inf, 12, 18, np.inf], labels=[1, 2, 3])

# Replace season string values with integer labels
season_mapping = {'winter': 1, 'spring': 2, 'summer': 3, 'fall': 4}
data['season'] = data['season'].map(season_mapping)

"""
Create a Bayesian Network model by specifying the relationships between variables as a list of tuples. 
Each tuple represents an edge in the network, with the first element being the parent node and the second element being the child node.
"""
model = BayesianNetwork([('season', 'temperature'),
                         ('hour', 'lights'),
                         ('hour', 'fan'),
                         ('temperature', 'fan'),
                         ('hour', 'heater_switch'),
                         ('temperature', 'heater_switch'),
                         ('temperature', 'ac_status'),
                         ('humidity', 'ac_status'),
                         ('season', "ac_status"),
                         ('distance_from_house', 'laundry_machine')])

# BDeu-Bayesian Dirichlet equivalent uniformwhat
model.fit(data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)

"""
 Returns the DiscreteFactor object, which can be printed to show the probability distribution of the device's state.
 it uses the Bayesian Network model to compute the probability distribution of the device's state, given the evidence. 
 This information can be used to make recommendations about how to control the device in the smart home system.
"""
def recommend_device(devices, evidence):
    threshold = 0.5
    result_array = []
    for device in devices:
        inference = VariableElimination(model)
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



evidence = {'hour': 1, 'temperature': 1, 'humidity': 2, 'distance_from_house': 1, 'season': 1}
# print(recommend_device(['lights','fan','ac_status'], evidence))
# print(recommend_device('fan', evidence))
# print(recommend_device('heater_switch', evidence))
# print(recommend_device('ac_status', evidence))
# print(recommend_device('laundry_machine', evidence))
