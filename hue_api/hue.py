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
from hue_api.scene import HueScene
from hue_api.exceptions import (UninitializedException,
                                ButtonNotPressedException,
                                DevicetypeException)


class HueApi:
    """
    Hue API Core class that keeps track of lights, groups, and scenes.

    First initialize an instance of this class. 
    Then, either `create_new_user` or `load_existing`.

    From there you can run all of the other methods that this class provides. 

    Attributes

    - `lights` (`[HueLight]`): List of `HueLight`
    - `groups` (`[HueGroup]`): List of `HueGroup`
    - `scenes` (`[HueScene]`): List of `HueScene`
    - `grouped_scenes` (`Dictionary[str, [HueScene]]`): Scene dict, grouped by scene name
    """

    def __init__(self):
        self.lights = []
        self.groups = []
        self.scenes = []
        self.grouped_scenes = {}

    def load_existing(self, cache_file=None, *args, **kwargs):
        """
        Load existing hue bridge user setting from `cache_file`.
        If no `cache_file` is provided, the `self.default_cache_file` method is used to make a cache file in the package's install directory.
        Finally, lastly, `self.default_cache_file` is used if not.

        After running this method, the API is authenticated and the Hue bridge can be interacted with.

        Args:
            cache_file (str, optional): Path to cache file. Defaults to `self.default_cache_file`.
        Raises:
            UninitializedException: Hue API could not be initialized
        """
        try:
            cache_file = cache_file or self.default_cache_file()
            with open(cache_file, 'rb') as cached_file:
                loaded = pickle.load(cached_file)
            bridge_ip_address = loaded.get('bridge_ip_address')
            user_name = loaded.get('user_name')
        except FileNotFoundError:
            raise UninitializedException
        self.bridge_ip_address = bridge_ip_address
        self.user_name = user_name
        self.base_url = f'http://{bridge_ip_address}/api/{user_name}'

    def default_cache_file(self) -> str:
        """
        Default cache file path, in the package's install directory.

        Returns:
            str: Cache file path
        """
        package_base_dir = inspect.getfile(hue_api)
        package_base_dir = os.path.dirname(package_base_dir)
        path = os.path.join(package_base_dir, '.pickle')
        return path

    def create_new_user(self, bridge_ip_address, *args, **kwargs):
        """
        Create a new API user for the Hue Bridge at the given IP address.

        Args:
            bridge_ip_address (str): The IP Address for the Hue Bridge

        Raises:
            DevicetypeException: the Hue Bridge at the given address does not support interfacing via this API.

            ButtonNotPressedException: the button on the Bridge was not pressed, so the attempt to connect to it has failed
        """
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

    def save_api_key(self, cache_file=None, *args, **kwargs):
        """
        Save the API key (username) to a cache file.

        Args:
            cache_file (str, optional): Path to cache file. Defaults to `self.default_cache_file`.
        """
        cache_file = cache_file or self.default_cache_file()
        with open(cache_file, 'wb') as pickle_file:
            cache = {
                'bridge_ip_address': self.bridge_ip_address,
                'user_name': self.user_name
            }
            pickle.dump(cache, pickle_file)

    def fetch_lights(self, *args, **kwargs):
        """
        Fetch available lights from the bridge.

        Returns:
            [HueLight]: List of available lights. Also saved to `self.lights`
        """
        url = self.base_url + "/lights"
        response = re.get(url).json()
        lights = []
        for id in response:
            state = response[id].get('state')
            name = response[id].get('name')
            hue_light = HueLight(int(id), name, state, url)
            lights.append(hue_light)
        self.lights = lights
        return lights

    def fetch_groups(self, *args, **kwargs):
        """
        Fetch available groups from the bridge

        Returns:
            [HueGroup]: List of available groups. Also saved to `self.groups`
        """
        url = self.base_url + "/groups"
        response = re.get(url).json()
        groups = []
        for id in response:
            group_name = response[id].get('name')
            lights = [int(light) for light in response[id].get('lights')]
            group_lights = self.filter_lights(lights)
            groups.append(HueGroup(id, group_name, group_lights))
        self.groups = groups
        return groups

    def fetch_scenes(self, *args, **kwargs):
        """
        Fetch available scenes from the bridge

        Returns:
            [HueScene]: List of available groups. Also saved to `self.scenes`
        """
        url = self.base_url + "/scenes"
        response = re.get(url).json()
        scenes = []
        for id in response:
            scene_name = response[id].get('name')
            lights = [int(light) for light in response[id].get('lights')]
            scene_lights = self.filter_lights(lights)
            scenes.append(HueScene(id, scene_name, scene_lights))
        self.scenes = scenes
        self.grouped_scenes = HueScene.group_scenes(scenes)
        return scenes

    def print_debug_info(self, *args, **kwargs):
        """
        Print some debug info about bridge.
        """
        print(f"Bridge IP address: {self.bridge_ip_address}")
        print(f"Bridge API key (username): {self.user_name}")
        print(f"API Base URL: {self.base_url}")

    def list_lights(self, *args, **kwargs):
        """
        Print debug info on all the lights from `self.lights`
        """
        for light in self.lights:
            print(light)

    def list_groups(self, *args, **kwargs):
        """
        Print debug info on all the groups from `self.groups`
        """
        for group in self.groups:
            print(group, "\n")

    def list_scenes(self, *args, **kwargs):
        """
        Print debug info on all the scenes from `self.scenes`
        """
        for scene in self.scenes:
            print(scene, "\n")

    def list_scene_groups(self, *args, **kwargs):
        """
        Print debug info on all the scenes from `self.grouped_scenes`.
        These scenes are in a `dict` of `{ scene_name(str) : [HueScene] }`
        """
        for group in self.grouped_scenes:
            print(f"\nScene group:{group}")
            for scene in self.grouped_scenes[group]:
                print(scene)

    def filter_lights(self, indices):
        """
        Return only certain lights, by id

        Args:
            indices ([int]): The ids of the lights we want

        Returns:
            [HueLight]: List of lights whose ids match `indices`
        """
        if not indices:
            return self.lights
        return [light for light in self.lights if light.id in indices]

    # Lights State Control

    def turn_on(self, indices=[]):
        """
        Turn on only those lights whose ids are provided

        Args:
            indices ([int], optional): Indices for the lights we want to turn on. Defaults to [].
        """
        for light in self.filter_lights(indices):
            light.set_on()

    def turn_off(self, indices=[]):
        """
        Turn off only those lights whose ids are provided

        Args:
            indices ([int], optional): Indices for the lights we want to turn off. Defaults to [].
        """
        for light in self.filter_lights(indices):
            light.set_off()

    def toggle_on(self, indices=[]):
        """
        Toggle on/pff only those lights whose ids are provided

        Args:
            indices ([int], optional): Indices for the lights we want to toggle. Defaults to [].
        """
        for light in self.filter_lights(indices):
            light.toggle_on()

    def set_brightness(self, brightness, indices=[]):
        """
        Set brightness on only those lights whose ids are provided

        Args:
            brightness (int or float): int value in range [0, 255], or float value in range [0, 1]
            indices ([int], optional): Indices for lights we want to set brightness on.
            Defaults to [].
        """
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
        """
        Set color for only those lights whose ids are provided

        Args:
            color (str): The webcolor name of the color we want to set the lights to
            indices ([int], optional): Ids of lights we want to set color on. Defaults to [].
        """
        if isinstance(color, str):
            color = webcolors.name_to_rgb(color)
            r = color[0] / 255
            g = color[1] / 255
            b = color[2] / 255
        else:
            r, g, b = color
        h, s, _ = colorsys.rgb_to_hsv(r, g, b)
        hue = int((2**16 - 1) * h)
        saturation = int((2**8 - 1) * s)
        for light in self.filter_lights(indices):
            light.set_color(hue, saturation)
