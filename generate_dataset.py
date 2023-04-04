import csv
import random
from datetime import date, datetime, timedelta

def generate_mock_data(start_date, end_date):
    data = []
    delta = timedelta(days=1)
    current_date = start_date

    while current_date <= end_date:
        season = get_season(current_date)
        for hour in [8, 14, 20]:  # Adjust the hours as needed
            timestamp = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour)
            outside_temperature = generate_temperature(season)
            air_conditioner_mode = "cool" if outside_temperature > 23 else "heat"

            entry = {
                "timestamp": str(timestamp),
                "lights": "on" if hour == 20 else "off",
                "fan": random.choice(["on", "off"]),
                "ac_status": random.choice(["on", "off"]),
                "ac_temperature": round(random.uniform(max(16, outside_temperature - 5), min(30, outside_temperature + 5)), 0),
                "ac_mode": air_conditioner_mode,
                "heater_switch": random.choice(["on", "off"]),
                "laundry_machine": random.choice(["on", "off"]),
                "temperature": outside_temperature,
                "humidity": round(random.uniform(0, 100), 1),
                "distance_from_house": round(random.uniform(0, 100), 1),
                "season": season
            }
            data.append(entry)
        current_date += delta

    return data

def get_season(date_obj):
    month = date_obj.month
    if 3 <= month < 6:
        return "spring"
    elif 6 <= month < 9:
        return "summer"
    elif 9 <= month < 12:
        return "fall"
    else:
        return "winter"

def generate_temperature(season):
    temperature_ranges = {
        "winter": (10, 15),
        "spring": (18, 26),
        "summer": (27, 30),
        "fall": (15, 25)
    }
    min_temp, max_temp = temperature_ranges[season]
    return round(random.uniform(min_temp, max_temp), 1)

def write_data_to_csv(data, filename):
    with open(filename, "w", newline="") as file:
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

start_date = date(2021, 1, 1)
end_date = date(2022, 12, 31)
mock_data = generate_mock_data(start_date, end_date)
write_data_to_csv(mock_data, "mock_data.csv")
