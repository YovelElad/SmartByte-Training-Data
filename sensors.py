from abc import ABC, abstractmethod
import numpy as np


class Sensor(ABC):
    @staticmethod
    @abstractmethod
    def name():
        pass

    @staticmethod
    @abstractmethod
    def bins():
        pass

    @staticmethod
    @abstractmethod
    def labels():
        pass


class TemperatureSensor(Sensor):
    @staticmethod
    def name():
        return "temperature"

    @staticmethod
    def bins():
        return [-np.inf, 15, 20, 25, 32, np.inf]

    @staticmethod
    def labels():
        return [1, 2, 3, 4, 5]


class HumiditySensor(Sensor):
    @staticmethod
    def name():
        return "humidity"

    @staticmethod
    def bins():
        return [-np.inf, 30, 60, 90, np.inf]

    @staticmethod
    def labels():
        return [1, 2, 3, 4]


class DistanceSensor(Sensor):
    @staticmethod
    def name():
        return "distance"

    @staticmethod
    def bins():
        return [-np.inf, 0.01, 20, np.inf]

    @staticmethod
    def labels():
        return [1, 2, 3]


class SoilSensor(Sensor):
    @staticmethod
    def name():
        return "soil"

    @staticmethod
    def bins():
        return [1850, 2200, 2800]

    @staticmethod
    def labels():
        return [1, 2]


class Manager(Sensor):
    @staticmethod
    def name():
        pass

    @staticmethod
    def bins():
        pass

    @staticmethod
    def labels():
        pass

    @staticmethod
    def get_list_of_devices():
        return ['lights', 'fan', 'ac_status', 'heater_switch', 'laundry_machine', 'pump']

    @staticmethod
    def get_list_of_devices_with_duration_postfix():
        return [device + "_duration" for device in Manager.get_list_of_devices()]

    @staticmethod
    def get_list_of_sensor_values():
        return ['hour', 'season', 'temperature', 'humidity', 'distance', 'soil']
