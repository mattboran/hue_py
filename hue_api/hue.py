import colorsys
import inspect
import json
import os
import pickle
import uuid

import requests as re
import webcolors

import hue_api
from hue_api.lights import HueLight
from hue_api.groups import HueGroup
from hue_api.exceptions import (UninitializedException,
                                ButtonNotPressedException,
                                DevicetypeException)


class HueApi:

    def __init__(self):
        self.lights = []
        self.groups = []

    def load_existing(self, *args, **kwargs):
        try:
            cache_file = kwargs.get('cache_file') or self.find_cache_file()
            with open(cache_file, 'rb') as cached_file:
                loaded = pickle.load(cached_file)
            bridge_ip_address = loaded.get('bridge_ip_address')
            user_name = loaded.get('user_name')
        except FileNotFoundError:
            raise UninitializedException
        self.bridge_ip_address = bridge_ip_address
        self.user_name = user_name
        self.base_url = f'http://{bridge_ip_address}/api/{user_name}'

    def find_cache_file(self):
        module_entry_point = inspect.getfile(hue_api)
        module_base_dir = os.path.dirname(module_entry_point)
        cache_file = os.path.join(module_base_dir, '.pickle')
        if not os.path.isfile(cache_file):
            raise FileNotFoundError
        return cache_file

    def create_new_user(self, bridge_ip_address, *args, **kwargs):
        url = f'http://{bridge_ip_address}/api'
        payload = {'devicetype': 'hue_cli'}
        response = re.post(url, json=payload)
        response = response.json()[0]
        error = response.get('error')
        if error:
            if error['type'] == 1:
                raise DevicetypeException
            else:
                raise ButtonNotPressedException
        user_name = response.get('success').get('username')
        self.user_name = user_name
        self.bridge_ip_address = bridge_ip_address
        self.base_url = f'http://{bridge_ip_address}/api/{user_name}'

    def save_api_key(self, *args, **kwargs):
        cache_file = kwargs.get('cache_file') or self.find_cache_file()
        with open(cache_file, 'wb') as pickle_file:
            cache = {
                'bridge_ip_address': self.bridge_ip_address,
                'user_name': self.user_name
            }
            pickle.dump(cache, pickle_file)

    def fetch_lights(self, *args, **kwargs):
        url = self.base_url + "/lights"
        response = re.get(url).json()
        lights = []
        for id in response:
            state = response[id].get('state')
            name = response[id].get('name')
            hue_light = HueLight(int(id), name, state, url)
            lights.append(hue_light)
        self.lights = lights

    def fetch_groups(self, *args, **kwargs):
        url = self.base_url + "/groups"
        response = re.get(url).json()
        groups = []
        for id in response:
            group_name = response[id].get('name')
            lights = [int(light) for light in response[id].get('lights')]
            group_lights = self.filter_lights(lights)
            groups.append(HueGroup(id, group_name, group_lights))
        self.groups = groups

    def print_debug_info(self, *args, **kwargs):
        print(f"Bridge IP address: {self.bridge_ip_address}")
        print(f"Bridge API key (username): {self.user_name}")
        print(f"API Base URL: {self.base_url}")

    def list_lights(self, *args, **kwargs):
        for light in self.lights:
            print(light)

    def list_groups(self, *args, **kwargs):
        for group in self.groups:
            print(group, "\n")

    def filter_lights(self, indices):
        if not indices:
            return self.lights
        return [light for light in self.lights if light.id in indices]

    # When no index is supplied, all the lights are turned on
    def turn_on(self, indices=[]):
        for light in self.filter_lights(indices):
            light.set_on()

    def turn_off(self, indices=[]):
        for light in self.filter_lights(indices):
            light.set_off()

    def toggle_on(self, indices=[]):
        for light in self.filter_lights(indices):
            light.toggle_on()

    def set_brightness(self, brightness, indices=[]):
        if isinstance(brightness, str):
            try:
                brightness = float(brightness)
            except ValueError:
                pass
            if brightness == 'max':
                brightness = 254
            elif brightness == 'min':
                brightness = 1
            elif brightness == 'med':
                brightness = 127
        if isinstance(brightness, float):
            if brightness <= 1.0:
                brightness *= 254
            brightness = int(brightness)
        for light in self.filter_lights(indices):
            light.set_brightness(brightness)

    def set_color(self, color, indices=[]):
        if isinstance(color, str):
            color = webcolors.name_to_rgb(color)
            r = color[0] / 255
            g = color[1] / 255
            b = color[2] / 255
        else:
            r, g, b = color
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        hue = int((2**16 - 1) * h)
        saturation = int((2**8 - 1) * s)
        for light in self.filter_lights(indices):
            light.set_color(hue, saturation)
