import pickle
import os
import requests

import pytest

from hue_api import HueApi
from hue_api.lights import HueLight
from hue_api.groups import HueGroup
from hue_api.exceptions import (UninitializedException,
                                DevicetypeException,
                                ButtonNotPressedException)


@pytest.fixture
def put_nothing(monkeypatch):
    """Requests.put() mocked to succeed and nothing else"""

    class MockResponse:
        status_code = 200

    def mock_put(*args, **kwargs):
        return MockResponse()
    monkeypatch.setattr(requests, "put", mock_put)

def test_defaults_dont_crash():
    api = HueApi()
    with pytest.raises(UninitializedException):
        api.load_existing()

def test_load_existing():
    test_cache_file = '.test'
    test_ip_address = 'test_address'
    test_user_name = 'test_user_name'
    api = HueApi()
    with pytest.raises(UninitializedException):
        api.load_existing(cache_file=test_cache_file)

    with open(test_cache_file, 'wb') as pickle_file:
        cache = {
            'bridge_ip_address': test_ip_address,
            'user_name': test_user_name,
        }
        pickle.dump(cache, pickle_file)
    api.load_existing(cache_file=test_cache_file)
    assert api.user_name == test_user_name
    assert api.bridge_ip_address == test_ip_address
    assert api.base_url == 'http://test_address/api/test_user_name'
    os.remove(test_cache_file)

def test_create_new(monkeypatch):
    test_user_name = 'test_user_name'
    test_address = 'test_address'

    class MockResponse:
        def __init__(self, data):
            self.data = data

        def json(self):
            return [self.data]

    def mock_post_success(*args, **kwargs):
        assert args[0] == 'http://test_address/api'
        assert kwargs['json'].get('devicetype')
        return MockResponse({
            'success': {'username': test_user_name}
        })

    def mock_post_device_type_error(*args, **kwargs):
        return MockResponse({
            'error': {'type': 1}
        })

    def mock_post_button_not_pressed(*args, **kwargs):
        return MockResponse({
            'error': {'type': 101}
        })

    api = HueApi()
    monkeypatch.setattr(requests, 'post', mock_post_success)
    api.create_new_user(test_address)
    assert api.bridge_ip_address == test_address
    assert api.user_name == test_user_name
    assert api.base_url == 'http://test_address/api/test_user_name'

    monkeypatch.setattr(requests, 'post', mock_post_device_type_error)
    with pytest.raises(DevicetypeException):
        api.create_new_user(test_address)

    monkeypatch.setattr(requests, 'post', mock_post_button_not_pressed)
    with pytest.raises(ButtonNotPressedException):
        api.create_new_user(test_address)

def test_save_api_key():
    test_cache_file = '.test'
    test_address = 'test_address'
    test_user_name = 'test_user_name'
    api = HueApi()
    api.bridge_ip_address = test_address
    api.user_name = test_user_name
    api.save_api_key(cache_file=test_cache_file)
    with open(test_cache_file, 'rb') as cache:
        loaded = pickle.load(cache)
    assert loaded == {
        'bridge_ip_address': test_address,
        'user_name': test_user_name
    }
    os.remove(test_cache_file)

def test_fetch_lights(monkeypatch):
    test_light_name = 'test light'

    class MockResponse:
        def json(self):
            return {
                '1': {
                    'name': test_light_name,
                    'state': {}
                }
            }

    test_url = 'http://test.com'

    def mock_get(*args, **kwargs):
        assert args[0] == test_url + '/lights'
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)
    api = HueApi()
    api.base_url = test_url
    api.fetch_lights()
    assert len(api.lights) == 1
    assert api.lights[0].name == test_light_name
    assert api.lights[0].id == 1

def test_fetch_groups(monkeypatch):
    test_group_name = 'test group'

    class MockResponse:
        def json(self):
            return {
                '1': {
                    'name': test_group_name,
                    'lights': [2],

                }
            }

    test_url = 'http://test.com'

    def mock_get(*args, **kwargs):
        assert args[0] == test_url + '/groups'
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)
    api = HueApi()
    api.lights = [
        HueLight(1, 'Light 1', {}, None),
        HueLight(2, 'light 2', {}, None)
    ]
    api.base_url = test_url
    api.fetch_groups()
    assert len(api.groups) == 1
    assert api.groups[0].id == '1'
    assert len(api.groups[0].lights) == 1
    assert api.groups[0].lights[0].id == 2
    assert api.groups[0].name == test_group_name


def test_fetch_scenes(monkeypatch):
    test_scene_name = 'test scene'

    class MockResponse:
        def json(self):
            return {
                '1': {
                    'name': test_scene_name,
                    'lights': [1],
                },
                '2': {
                    'name': test_scene_name,
                    'lights': [2]
                }
            }

    test_url = 'http://test.com'

    def mock_get(*args, **kwargs):
        assert args[0] == test_url + '/scenes'
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)
    api = HueApi()
    api.lights = [
        HueLight(1, 'Light 1', {}, None),
        HueLight(2, 'light 2', {}, None)
    ]
    api.base_url = test_url
    api.fetch_scenes()
    assert len(api.scenes) == 2
    assert len(api.grouped_scenes) == 1
    assert len(api.scenes[0].lights) == 1
    assert len(api.scenes[1].lights) == 1
    assert len(api.grouped_scenes[test_scene_name]) == 2

def test_filter_lights():
    api = HueApi()
    api.lights = [
        HueLight(1, 'Light 1', {}, None),
        HueLight(2, 'light 2', {}, None)
    ]
    assert len(api.filter_lights(None)) == 2
    assert len(api.filter_lights([1])) == 1
    assert api.filter_lights([1])[0].id == 1
    assert api.filter_lights([2])[0].id == 2
    assert api.filter_lights([1, 2]) == api.lights

def test_turn_on_off(put_nothing):
    api = HueApi()
    api.lights = [
        HueLight(1, 'Light 1', {}, None),
        HueLight(2, 'light 2', {}, None)
    ]
    for light in api.lights:
        assert not light.state.is_on
    api.turn_on()
    for light in api.lights:
        assert light.state.is_on
    api.turn_off([1])
    assert not api.lights[0].state.is_on
    assert api.lights[1].state.is_on

def test_toggle_on(put_nothing):
    api = HueApi()
    api.lights = [
        HueLight(1, 'Light 1', {'on': False}, None),
    ]
    light = api.lights[0]
    assert not light.state.is_on
    api.toggle_on()
    assert light.state.is_on
    api.toggle_on()
    assert not light.state.is_on

def test_set_brightness(put_nothing):
    api = HueApi()
    api.lights = [
        HueLight(1, 'Light 1', {'bri': 1}, None),
    ]
    light = api.lights[0]
    assert light.state.brightness == 1
    api.set_brightness(100)
    assert light.state.brightness == 100
    api.set_brightness('max')
    assert light.state.brightness == 254

def test_set_color(put_nothing):
    api = HueApi()
    api.lights = [
        HueLight(1, 'Light 1', {'hue': 0, 'sat': 0}, None),
    ]
    light = api.lights[0]
    assert light.state.hue == 0
    assert light.state.saturation == 0
    api.set_color('red')
    assert light.state.hue == 0
    assert light.state.saturation == 255
    api.set_color('green')
    assert light.state.hue == 21845
    assert light.state.saturation == 255
