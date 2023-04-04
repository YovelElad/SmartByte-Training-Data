import pandas as pd
from pomegranate import BayesianNetwork
from sklearn.model_selection import train_test_split

# Load the dataset
df = pd.read_csv("mock_data.csv")

# Convert 'season' to numerical values
df['season'] = df['season'].map({'winter': 0, 'spring': 1, 'summer': 2, 'fall': 3})

# Convert 'ac_mode' to numerical values
df['ac_mode'] = df['ac_mode'].map({'heat': 0, 'cool': 1})

# Extract hour from the timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour

# Drop the 'timestamp' column as it's no longer needed
df.drop(columns=['timestamp'], inplace=True)

# Round float columns to integers
float_columns = ['ac_temperature', 'temperature', 'humidity', 'distance_from_house']
for col in float_columns:
    df[col] = df[col].round().astype(int)

# Split the dataset into training and testing sets
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Convert the training set to a NumPy array
train_data = train_df.values

structure = (
    (10, 11),  # lights
    (7, 10),   # fan
    (3, 7, 10),  # ac_status
    (7,),      # ac_temperature
    (7,),      # ac_mode
    (0, 7, 10),  # heater_switch
    (7, 10),     # laundry_machine
    (7, 10),     # temperature
    (7, 10),     # humidity
    (),         # distance_from_house (independent)
    (),         # season (independent)
    ()          # hour (independent)
)


column_names = ['lights', 'fan', 'ac_status', 'ac_temperature', 'ac_mode', 'heater_switch', 'laundry_machine',
                'temperature', 'humidity', 'distance_from_house', 'season', 'hour']

# Train the Bayesian Network
model = BayesianNetwork.from_samples(train_data, algorithm='exact', state_names=column_names)

# Set the desired values for distance_from_house, season, and hour
distance_from_house = 5
season = 1  # spring
hour = 14




evidence = [[None, None, None, None, None, None, None, None, None, distance_from_house, season, hour]]

# Perform inference
predictions = model.predict_proba(evidence)

def get_most_probable_state(distribution):
    return max(distribution.parameters[0], key=distribution.parameters[0].get)

# Get the most probable states for each variable
most_probable_lights_status = get_most_probable_state(predictions[0])
most_probable_ac_status = get_most_probable_state(predictions[2])
most_probable_ac_temperature = get_most_probable_state(predictions[3])
most_probable_ac_mode = get_most_probable_state(predictions[4])
most_probable_heater_status = get_most_probable_state(predictions[5])
most_probable_laundry_machine_status = get_most_probable_state(predictions[6])

# Print the results
print(f"The most probable lights status is: {most_probable_lights_status}")
print(f"The most probable AC status is: {most_probable_ac_status}")
