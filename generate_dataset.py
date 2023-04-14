import csv
import random
from datetime import date, datetime, timedelta

def append_data_to_csv(row_data, filename):
    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(row_data['data'].values())



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
            ac_energy, ac_duration = generate_ac_energy_and_duration(season, current_date.month, hour)
            heater_energy, heater_duration = generate_heater_energy_and_duration(season, current_date.month, hour)
            lights_energy, lights_duration = generate_lights_energy_and_duration(hour)
            laundry_energy, laundry_duration = generate_laundry_energy_and_duration()

            entry = {
                "timestamp": str(timestamp),
                "lights": "on" if hour == 20 else "off",
                "fan": "on" if (season == "summer" and hour in [12, 18, 20]) else random.choice(["on", "off"]),
                "ac_status": "on" if ((season in ["summer", "spring"] and outside_temperature <= 20) or (
                            season == "winter" and outside_temperature >= 26) or (
                                                  season == "fall" and outside_temperature >= 22)) else "off",
                "ac_temperature": round(random.uniform(max(16, outside_temperature - 5), min(30, outside_temperature + 5)), 0),
                "ac_mode": air_conditioner_mode,
                "heater_switch": "on" if (season in ["winter", "fall"] and hour == 20) or random.random() < 0.5 else "off",
                "laundry_machine": "on" if (hour in [8, 20] and distance_from_house <= 0.01) else "off",
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

def generate_ac_energy_and_duration(season, month, hour):
    if season in ["summer", "spring"]:
        if month in [7, 8]:
            base_energy = 30
            base_duration = 180
        else:
            base_energy = 15
            base_duration = 90

        if hour in [14, 20]:
            energy = round(random.uniform(base_energy, base_energy * 2), 2)
            duration = round(random.uniform(base_duration, base_duration * 2), 1)
        else:
            energy = round(random.uniform(base_energy / 2, base_energy), 2)
            duration = round(random.uniform(base_duration / 2, base_duration), 1)
    else:
        energy = round(random.uniform(2, 10), 2)
        duration = round(random.uniform(15, 45), 1)

    return energy, duration

def generate_heater_energy_and_duration(season, month, hour):
    if season in ["winter", "fall"]:
        if month == 1:
            base_energy = 40
            base_duration = 240
        else:
            base_energy = 20
            base_duration = 120

        if hour == 20:
            energy = round(random.uniform(base_energy, base_energy * 2), 2)
            duration = round(random.uniform(base_duration, base_duration * 2), 1)
        else:
            energy = round(random.uniform(base_energy / 2, base_energy), 2)
            duration = round(random.uniform(base_duration / 2, base_duration), 1)
    else:
        energy = round(random.uniform(5, 10), 2)
        duration = round(random.uniform(10, 30), 1)

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
        "winter": (12, 15),
        "spring": (18, 25),
        "summer": (25, 30),
        "fall": (15, 24)
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

start_date = date(2020, 4, 12)
end_date = date(2023, 4, 12)
mock_data = generate_mock_data(start_date, end_date)
write_data_to_csv(mock_data, "mock_data.csv")
