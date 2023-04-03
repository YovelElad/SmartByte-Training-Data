# import random

# # set the number of data points to generate
# num_data_points = 100

# # set the location coordinates
# location_lat = 37.7749
# location_lon = -122.4194

# # set the maximum distance in kilometers
# max_distance = 20

# # generate random distance and time data
# data = []
# for i in range(num_data_points):
#     # generate a random distance from the location in kilometers
#     distance = round(random.uniform(0, max_distance), 10)

#     # generate a random time spent at the distance in minutes
#     time = random.randint(0, 120)

#     # add the data point to the list
#     data.append((distance, time))

# # print the data in a table
# print("Distance (in kilometers) | Time (in minutes)")
# print("----------------------- | -----------------")
# for d in data:
#     print("{:.10f}            | {}".format(d[0], d[1]))



# import random
# import datetime
# import json

# # set the number of data points to generate
# num_data_points = 100

# # set the location coordinates
# location_lat = 37.7749
# location_lon = -122.4194

# # set the maximum distance in kilometers
# max_distance = 1.3

# # set the start date and time
# start_date = datetime.datetime(2022, 1, 1)
# start_time = datetime.time(0, 0)

# # generate random distance, time, and timestamp data
# data = []
# for i in range(num_data_points):
#     # generate a random distance from the location in kilometers
#     distance = round(random.uniform(0, max_distance), 10)

#     # generate a random time spent at the distance in minutes
#     time = random.randint(0, 120)

#     # generate a random timestamp within a one-year period
#     timestamp = start_date + datetime.timedelta(days=random.randint(0, 365), seconds=random.randint(0, 86400))
#     timestamp = datetime.datetime.combine(timestamp.date(), start_time) + datetime.timedelta(seconds=timestamp.second)

#     # add the data point to the list as a dictionary
#     data.append({'timestamp': timestamp.isoformat(), 'distance': distance, 'time': time})

# # write the data to a JSON file
# with open('data.json', 'w') as outfile:
#     json.dump(data, outfile)

# import random
# import datetime
# import json

# # set the number of data points to generate
# num_data_points = 100

# # set the location coordinates
# location_lat = 37.7749
# location_lon = -122.4194

# # set the maximum distance in kilometers
# max_distance = 2

# # set the start date and time
# start_date = datetime.datetime(2023, 1, 1)
# start_time = datetime.time(0, 0)

# # set the end date and time
# end_date = datetime.datetime(2023, 4, 1)
# end_time = datetime.time(0, 0)

# # generate random distance, time, and timestamp data
# data = []
# for i in range(num_data_points):
#     # generate a random distance from the location in kilometers
#     if datetime.time(6, 0) <= start_time <= datetime.time(18, 0):
#         # if it's between 6 am and 6 pm, allow any distance up to the maximum
#         distance = round(random.uniform(0, max_distance), 10)
#     else:
#         # if it's between 6 pm and 6 am, limit the distance to 0.0000001 km
#         distance = round(random.uniform(0, 0.00001), 10)

#     # generate a random time spent at the distance in minutes
#     time = random.randint(0, 120)

#     # generate a random timestamp between the start and end date and time
#     timestamp = datetime.datetime.combine(start_date, start_time) + datetime.timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))

#     # add the data point to the list if it falls within the date range
#     if timestamp < end_date:
#         # add the data point to the list as a dictionary
#         data.append({'timestamp': timestamp.isoformat(), 'distance': distance, 'time': time})

#     # increment the start time by a random number of seconds between 1 and 600 (10 minutes)
#     start_time = (datetime.datetime.min + datetime.timedelta(seconds=random.randint(1, 600))).time()

# # sort the data by timestamp
# data = sorted(data, key=lambda x: x['timestamp'])

# # write the data to a JSON file
# with open('data.json', 'w') as outfile:
#     json.dump(data, outfile)

import random
import datetime
import json

# set the number of data points to generate
num_data_points = 120

# set the location coordinates
location_lat = 37.7749
location_lon = -122.4194

# set the maximum distance in kilometers
max_distance = 2

# set the start date and time
start_date = datetime.date(2023, 1, 1)
start_time = datetime.time(0, 0)

# set the end date and time
end_date = start_date + datetime.timedelta(days=120)
end_time = datetime.time(0, 0)

# generate random distance, time, and timestamp data
data = []
current_date = start_date
while current_date <= end_date:
    # generate a random number of data points for the current date
    num_points = random.randint(1, 5)
    for i in range(num_points):
        # generate a random distance from the location in kilometers
        if datetime.time(6, 0) <= start_time <= datetime.time(18, 0):
            # if it's between 6 am and 6 pm, allow any distance up to the maximum
            distance = round(random.uniform(0, max_distance), 10)
        else:
            # if it's between 6 pm and 6 am, limit the distance to 0.0000001 km
            distance = round(random.uniform(0, 0.0000001), 10)

        # generate a random time spent at the distance in minutes
        time = random.randint(0, 120)

        # generate a random timestamp for the current date
        timestamp = datetime.datetime.combine(current_date, start_time) + datetime.timedelta(seconds=random.randint(0, 86399))

        # add the data point to the list
        data.append({'timestamp': timestamp.isoformat(), 'distance': distance, 'time': time})

        # increment the start time by a random number of seconds between 1 and 600 (10 minutes)
        start_time = (datetime.datetime.min + datetime.timedelta(seconds=random.randint(1, 600))).time()

    # increment the current date by 1 day
    current_date += datetime.timedelta(days=1)

# sort the data by timestamp
data = sorted(data, key=lambda x: x['timestamp'])

# write the data to a JSON file
with open('data.json', 'w') as outfile:
    json.dump(data, outfile)