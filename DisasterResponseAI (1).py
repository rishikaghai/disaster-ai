

# Note: You'll need to sign up for free API keys from OpenWeatherMap and OpenCage Geocoder


# DisasterResponseAI.py

import random
import math
from collections import defaultdict
import requests
import json
from datetime import datetime, timedelta

# Note: You'll need to sign up for free API keys from OpenWeatherMap and OpenCage Geocoder

WEATHER_API_KEY = "8fa7ea1ea00dfaa19d8b0124458917f0"
GEOCODE_API_KEY = "ddb49a5020c34b5da871dcc780a1785a"

class DisasterZone:
    def __init__(self, name, latitude, longitude, population):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.population = population
        self.risk_level = 0
        self.resources = defaultdict(int)

class DisasterResponseAI:
    def __init__(self):
        self.zones = []
        self.knowledge_base = {
            'flood': {'required_resources': ['boats', 'sandbags', 'pumps'], 'evacuation_threshold': 0.7},
            'hurricane': {'required_resources': ['shelters', 'food_supplies', 'generators'], 'evacuation_threshold': 0.8},
            'earthquake': {'required_resources': ['search_teams', 'medical_supplies', 'temporary_housing'], 'evacuation_threshold': 0.9},
            'wildfire': {'required_resources': ['fire_engines', 'water_bombers', 'fire_retardant'], 'evacuation_threshold': 0.75}
        }

    def add_zone(self, zone):
        self.zones.append(zone)

    def get_weather_forecast(self, lat, lon):
        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching weather data: {response.status_code}")
            return None

    def geocode_location(self, location_name):
        url = f"https://api.opencagedata.com/geocode/v1/json?q={location_name}&key={GEOCODE_API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            results = response.json()['results']
            if results:
                return results[0]['geometry']
        print(f"Error geocoding location: {response.status_code}")
        return None

    def assess_risk(self, zone, disaster_type):
        # weather = self.get_weather_forecast(zone.latitude, zone.longitude)
        # if not weather:
        #     return 0

        # risk = 0
        # for forecast in weather['list'][:8]:  # Consider next 24 hours
        #     if disaster_type == 'flood':
        #         if 'rain' in forecast and forecast['rain'].get('3h', 0) > 20:  # More than 20mm rain in 3 hours
        #             risk += 0.2
        #     elif disaster_type == 'hurricane':
        #         if forecast['wind']['speed'] > 30:  # Wind speed over 30 m/s
        #             risk += 0.25
        #     elif disaster_type == 'wildfire':
        #         if forecast['main']['temp'] > 35 and forecast['main']['humidity'] < 30:  # Hot and dry
        #             risk += 0.3
        return random.uniform(0.1, 0.9)

    def allocate_resources(self, disaster_type):
        required_resources = self.knowledge_base[disaster_type]['required_resources']
        for zone in self.zones:
            for resource in required_resources:
                allocation = int(zone.risk_level * 100)  # Scale up for visibility
                zone.resources[resource] = allocation

    def recommend_actions(self, disaster_type):
        actions = []
        for zone in self.zones:
            if zone.risk_level >= self.knowledge_base[disaster_type]['evacuation_threshold']:
                actions.append(f"URGENT: Evacuate {zone.name}")
            elif zone.risk_level >= 0.5:
                actions.append(f"WARNING: Prepare for possible evacuation in {zone.name}")
            actions.append(f"Deploy {zone.resources} to {zone.name}")
        return actions

    def heuristic_search_safest_route(self, start_zone, end_zone):
        def distance(z1, z2):
            return math.sqrt((z1.latitude - z2.latitude)**2 + (z1.longitude - z2.longitude)**2)

        def heuristic(zone):
            return distance(zone, end_zone) * (1 + zone.risk_level)

        open_set = {start_zone}
        came_from = {}
        g_score = {start_zone: 0}  #actual cost of path from to b
        f_score = {start_zone: heuristic(start_zone)}  #total best path

        while open_set:
            current = min(open_set, key=lambda z: f_score[z])
            if current == end_zone:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_zone)
                return list(reversed(path))

            open_set.remove(current)
            for neighbor in self.zones:
                tentative_g_score = g_score[current] + distance(current, neighbor)
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor)
                    open_set.add(neighbor)

        return None
