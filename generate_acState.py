# import random
# import datetime
# import json

# # set the number of data points to generate
# num_data_points = 120

# # set the start date and time
# start_date = datetime.date(2023, 1, 1)
# start_time = datetime.time(0, 0)

# # set the end date and time
# end_date = start_date + datetime.timedelta(days=120)
# end_time = datetime.time(0, 0)

# # generate random AC state and timestamp data
# data = []
# current_date = start_date
# while current_date <= end_date:
#     # generate a random timestamp for the current date
#     timestamp = datetime.datetime.combine(current_date, start_time) + datetime.timedelta(seconds=random.randint(0, 86399))
    
#     # determine the AC state based on the current time
#     if datetime.time(19, 0) <= timestamp.time() <= datetime.time(22, 0):
#         ac_state = 1
#     else:
#         ac_state = 0
    
#     # add the data point to the list
#     data.append({'timestamp': timestamp.isoformat(), 'ac_state': ac_state})
    
#     # increment the start time by a random number of seconds between 1 and 600 (10 minutes)
#     start_time = (datetime.datetime.min + datetime.timedelta(seconds=random.randint(1, 600))).time()
    
#     # increment the current date by 1 day
#     current_date += datetime.timedelta(days=1)

# # sort the data by timestamp
# data = sorted(data, key=lambda x: x['timestamp'])

# # write the data to a JSON file
# with open('ac_data.json', 'w') as outfile:
#     json.dump(data, outfile)



import random
from datetime import datetime, timedelta
import json

devices = [
    {'id': 1, 'name': 'Ac', 'state': 'off'}
    # {'id': 2, 'name': 'Heater', 'state': 'off'},
    # {'id': 3, 'name': 'Laundry', 'state': 'off'},
    # add more devices here as needed
]

# generate data for 4 months (120 days)
start_time = datetime(2023, 1, 1)
end_time = datetime(2023, 4, 1)
delta = timedelta(minutes=1)

# create a list to hold the data
data = []


for device in devices:
    state = device['state']
    device_id = device['id']
    device_name = device['name']
    last_switch_time = start_time
    while last_switch_time < end_time:
        # generate a random switch time
        if last_switch_time.hour >= 19 and last_switch_time.hour < 21:
            switch_time = last_switch_time + timedelta(hours=1)
        else:
            switch_time = last_switch_time + timedelta(hours=random.randint(4, 8))
        # make sure the switch time is within the day
        if switch_time >= end_time:
            break
        # determine the new state
        if state == 'on':
            state = 'off'
            # add duration to previous row if applicable
            for i in range(len(data)):
                if data[i]['device_id'] == device_id and data[i]['time'] == last_switch_time and state == 'off':
                    # calculate the duration of the on-time and add it to the previous row
                    on_duration = switch_time - last_switch_time
                    data[i]['duration'] = on_duration.total_seconds() / 60
                    break
        else:
            state = 'on'
            data.append({'device_id': device_id, 'device_name': device_name, 'time': switch_time})
        last_switch_time = switch_time

# add duration to last row if applicable
for i in range(len(data)):
    if data[i]['device_id'] == device_id and data[i]['time'] == last_switch_time and state == 'on':
        # calculate the duration of the on-time and add it to the previous row
        on_duration = end_time - last_switch_time
        data[i]['duration'] = on_duration.total_seconds()
        break



def datetime_encoder(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return None
with open('devices_states.json', 'w') as f:
    json.dump(data, f, default=datetime_encoder)