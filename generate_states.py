import random
from datetime import datetime, timedelta
import json

devices = [
    {'id': 1, 'name': 'Ac', 'state': 'off'}
    # {'id': 2, 'name': 'Heater', 'state': 'off'},
    # {'id': 3, 'name': 'Laundry', 'state': 'off'},
    # add more devices here as needed
]

# generate data for a month (30 days)
start_time = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
end_time = start_time + timedelta(days=30)
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
    