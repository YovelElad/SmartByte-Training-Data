import pandas as pd
from pomegranate import BayesianNetwork
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import networkx as nx



def create_evidence_list(df, distance_from_house, season, hour):
    evidence = df.iloc[0].copy()
    for col in evidence.index:
        evidence[col] = None

    evidence['distance_from_house'] = distance_from_house
    evidence['season'] = {'winter': 0, 'spring': 1, 'summer': 2, 'fall': 3}[season]
    evidence['hour'] = hour

    return [evidence.tolist()[:-1]]  # Exclude the last element (hour) from the list



# Define a function to get the most probable value from a continuous variable's distribution
def get_most_probable_value(distribution):
    mu = distribution.parameters[0]['mean']
    return round(mu)

# Define a function to get the most probable state for categorical variables
def get_most_probable_state(distribution):
    return max(distribution.parameters[0], key=distribution.parameters[0].get)

# Add the generate_recommendations function
def generate_recommendations(current_states, predicted_states):
    recommendations = []
    for device, current_state, predicted_state in zip(column_names, current_states, predicted_states):
        if current_state != predicted_state:
            if device in ['ac_temperature']:
                action = f"change to {predicted_state}"
            else:
                action = "turn on" if predicted_state == "on" else "turn off"
            recommendations.append(f"Recommended action for {device}: {action}")
    return recommendations




# Load the dataset
df = pd.read_csv("mock_data.csv")

# # Convert 'season' to numerical values
# df['season'] = df['season'].map({'winter': 0, 'spring': 1, 'summer': 2, 'fall': 3})
#
# # Convert 'ac_mode' to numerical values
# df['ac_mode'] = df['ac_mode'].map({'heat': 0, 'cool': 1})

# Extract hour from the timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour

# Drop the 'timestamp' column as it's no longer needed
df.drop(columns=['timestamp'], inplace=True)

# Round float columns to integers
float_columns = ['ac_temperature', 'temperature', 'humidity', 'distance_from_house']
for col in float_columns:
    df[col] = df[col].round().astype(int)





categorical_columns = ['lights', 'fan', 'ac_status', 'ac_mode', 'heater_switch', 'laundry_machine']
# ... (all other preprocessing steps)

# Normalize energy consumption and duration columns
scaler = MinMaxScaler()
energy_duration_columns = ['ac_energy', 'ac_duration', 'heater_energy', 'heater_duration', 'lights_energy', 'lights_duration', 'laundry_energy', 'laundry_duration']
df[energy_duration_columns] = scaler.fit_transform(df[energy_duration_columns])

# Split the dataset into training and testing sets
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)


# Split the dataset into training and testing sets
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# # Convert the training set to a NumPy array
# train_data = train_df.values
# train_data = pd.get_dummies(train_data, columns=categorical_columns)
# print("train_data shape:", train_data.shape)

# Convert the training set to one-hot encoded columns

train_df = pd.get_dummies(train_df, columns=categorical_columns)

# Convert the testing set to one-hot encoded columns
test_df = pd.get_dummies(test_df, columns=categorical_columns)
print("train_df.columns:",train_df.columns)

train_data = train_df.values
print("train_data shape:", train_data.shape)


# Discretize continuous variables
train_df['ac_temperature_discrete'] = pd.cut(train_df['ac_temperature'], bins=5, labels=False)
train_df['temperature_discrete'] = pd.cut(train_df['temperature'], bins=5, labels=False)
train_df['humidity_discrete'] = pd.cut(train_df['humidity'], bins=5, labels=False)
train_df['distance_from_house_discrete'] = pd.cut(train_df['distance_from_house'], bins=5, labels=False)
train_df['hour_discrete'] = pd.cut(train_df['hour'], bins=6, labels=False)

test_df['ac_temperature_discrete'] = pd.cut(test_df['ac_temperature'], bins=5, labels=False)
test_df['temperature_discrete'] = pd.cut(test_df['temperature'], bins=5, labels=False)
test_df['humidity_discrete'] = pd.cut(test_df['humidity'], bins=5, labels=False)
test_df['distance_from_house_discrete'] = pd.cut(test_df['distance_from_house'], bins=5, labels=False)
test_df['hour_discrete'] = pd.cut(test_df['hour'], bins=6, labels=False)

# Drop the original continuous variables
train_df.drop(columns=['ac_temperature', 'temperature', 'humidity', 'distance_from_house', 'hour'], inplace=True)
test_df.drop(columns=['ac_temperature', 'temperature', 'humidity', 'distance_from_house', 'hour'], inplace=True)



structure =[
    ('lights_off', 'lights_on'),          # lights
    ('fan_off', 'fan_on'),                # fan
    ('ac_status_off', 'ac_status_on'),    # ac_status
    ('ac_temperature_discrete',),         # ac_temperature
    ('ac_mode_cool', 'ac_mode_heat'),     # ac_mode
    ('heater_switch_off', 'heater_switch_on'),  # heater_switch
    ('laundry_machine_off', 'laundry_machine_on'),  # laundry_machine
    ('temperature_discrete',),            # temperature
    ('humidity_discrete',),               # humidity
    ('distance_from_house_discrete',),    # distance_from_house (independent)
    ('season',),                          # season (independent)
    ('hour_discrete',),                   # hour (independent)
]


column_names = train_df.columns.tolist()

# Train the Bayesian Network
# Create the constraint graph
constraint_graph = nx.DiGraph()

constraint_graph.add_edge('lights_on', 'lights_energy')
constraint_graph.add_edge('fan_on', 'fan_energy')
constraint_graph.add_edge('ac_status_on', 'ac_energy')
constraint_graph.add_edge('ac_status_on', 'ac_duration')
constraint_graph.add_edge('ac_temperature', 'ac_energy')
constraint_graph.add_edge('ac_mode_cool', 'ac_energy')
constraint_graph.add_edge('heater_switch_on', 'heater_energy')
constraint_graph.add_edge('heater_switch_on', 'heater_duration')
constraint_graph.add_edge('laundry_machine_on', 'laundry_energy')
constraint_graph.add_edge('laundry_machine_on', 'laundry_duration')
constraint_graph.add_edge('temperature', 'ac_energy')
constraint_graph.add_edge('humidity', 'ac_energy')

model = BayesianNetwork.from_samples(
    train_data,
    algorithm='exact',
    state_names=column_names,
    constraint_graph=constraint_graph,
)

print("after model")
# Set the desired values for distance_from_house, season, and hour
distance_from_house = 0.01
season = "spring"   # spring
hour = 14



evidence = create_evidence_list(train_df, distance_from_house, season, hour)

print("Evidence:", evidence)
print("Model structure:", model.structure)

# evidence = [[None, None, None, None, None, None, None, None, None, distance_from_house, season, hour]]

try:
    predictions = model.predict_proba(evidence)
except ValueError as e:
    if "State 'distance_from_house' does not have key '5'" in str(e):
        print("Error: The 'distance_from_house' variable does not have the key '5' in the dataset. Please use a valid value.")
    else:
        raise e





state_names = [state.name for state in model.states]

ac_temperature_index = model.states.index(model.states[state_names.index('ac_temperature')])

print("ac_temperature_index:", ac_temperature_index)
print("len(predictions):", len(predictions))

most_probable_ac_temperature = get_most_probable_value(predictions[ac_temperature_index])

most_probable_lights_status = 'on' if predictions[state_names.index('lights_on')].parameters[0]['on'] > predictions[state_names.index('lights_off')].parameters[0]['off'] else 'off'
most_probable_ac_status = 'on' if predictions[state_names.index('ac_status_on')].parameters[0]['on'] > predictions[state_names.index('ac_status_off')].parameters[0]['off'] else 'off'
most_probable_ac_mode = 'cool' if predictions[state_names.index('ac_mode_cool')].parameters[0]['cool'] > predictions[state_names.index('ac_mode_heat')].parameters[0]['heat'] else 'heat'
most_probable_heater_status = 'on' if predictions[state_names.index('heater_switch_on')].parameters[0]['on'] > predictions[state_names.index('heater_switch_off')].parameters[0]['off'] else 'off'
most_probable_laundry_machine_status = 'on' if predictions[state_names.index('laundry_machine_on')].parameters[0]['on'] > predictions[state_names.index('laundry_machine_off')].parameters[0]['off'] else 'off'




# Provide the current states of the devices
current_lights_status = "off"
current_ac_status = "on"
current_ac_temperature = 22
current_ac_mode = "cool"
current_heater_status = "off"
current_laundry_machine_status = "off"

current_states = [current_lights_status, None, current_ac_status, current_ac_temperature, current_ac_mode, current_heater_status, current_laundry_machine_status, None, None, None, None, None]

# Call the generate_recommendations function
predicted_states = [most_probable_lights_status, None, most_probable_ac_status, most_probable_ac_temperature, most_probable_ac_mode, most_probable_heater_status, most_probable_laundry_machine_status, None, None, None, None, None]
recommendations = generate_recommendations(current_states, predicted_states)


print('before recommnadations::')
# Print the recommendations
for recommendation in recommendations:
    print(recommendation)
