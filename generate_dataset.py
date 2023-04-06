import csv
import random
from datetime import date, datetime, timedelta

def generate_mock_data(start_date, end_date):
    data = []
    delta = timedelta(days=1)
    current_date = start_date

    while current_date <= end_date:
        season = get_season(current_date)
        for hour in [8,12, 14,18, 20]:  # Adjust the hours as needed
            timestamp = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour)
            outside_temperature = generate_temperature(season)
            air_conditioner_mode = "cool" if outside_temperature > 23 else "heat"

            distance_from_house = generate_distance_from_house(season, hour)

            ac_energy, ac_duration = generate_ac_energy_and_duration(season, hour)
            heater_energy, heater_duration = generate_heater_energy_and_duration(season, hour)
            lights_energy, lights_duration = generate_lights_energy_and_duration(hour)
            laundry_energy, laundry_duration = generate_laundry_energy_and_duration()

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
                "distance_from_house": distance_from_house,
                "season": season,
                "ac_energy": ac_energy,
                "ac_duration": ac_duration,
                "heater_energy": heater_energy,
                "heater_duration": heater_duration,
                "lights_energy": lights_energy,
                "lights_duration": lights_duration,
                "laundry_energy": laundry_energy,
                "laundry_duration": laundry_duration
            }
            data.append(entry)
        current_date += delta

    return data

def generate_distance_from_house(season, hour):
    if hour in [8, 14]:
        # Higher distance (above 20 km) during 8 and 14 o'clock
        distance = round(random.uniform(20, 100), 1)
    else:
        if season == "winter":
            # Shorter distance (below 0.01 km) most of the time during winter
            distance = round(random.uniform(0, 0.01), 4)
        else:
            # Shorter distance (below 0.01 km) most of the time during other seasons
            distance = round(random.uniform(0, 0.01), 4) if random.random() < 0.9 else round(random.uniform(0.01, 20), 1)
    return distance

def generate_lights_energy_and_duration(hour):
    if hour == 20:
        energy = round(random.uniform(10, 20), 2)
        duration = round(random.uniform(180, 300), 1)
    else:
        energy = round(random.uniform(2, 10), 2)
        duration = round(random.uniform(30, 120), 1)

    return energy, duration

def generate_laundry_energy_and_duration():
    energy = round(random.uniform(10, 40), 2)
    duration = round(random.uniform(30, 180), 1)

    return energy, duration

def generate_ac_energy_and_duration(season, hour):
    if season == "summer" or season == "spring":
        if hour == 14 or hour == 20:
            energy = round(random.uniform(10, 30), 2)
            duration = round(random.uniform(60, 180), 1)
        else:
            energy = round(random.uniform(5, 15), 2)
            duration = round(random.uniform(30, 90), 1)
    else:
        energy = round(random.uniform(2, 10), 2)
        duration = round(random.uniform(15, 45), 1)

    return energy, duration

def generate_heater_energy_and_duration(season, hour):
    if season == "winter":
        if hour == 20:
            energy = round(random.uniform(20, 40), 2)
            duration = round(random.uniform(120, 240), 1)
        else:
            energy = round(random.uniform(10, 20), 2)
            duration = round(random.uniform(60, 120), 1)
    else:
        energy = round(random.uniform(5, 10), 2)
        duration = round(random.uniform(30, 60), 1)

    return energy, duration


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

start_date = date(2022, 1, 1)
end_date = date(2022, 12, 31)
mock_data = generate_mock_data(start_date, end_date)
write_data_to_csv(mock_data, "mock_data.csv")
