import colorsys
import requests as re

from hue_api.exceptions import FailedToGetState, FailedToSetState
from hue_api.state import LightState

class HueLight:

    # Public methods

    def __init__(self, id, name, state_dict, base_url):
        self.id = id
        self.name = name
        self.light_url = f"{base_url}/{id}/"
        self.state = LightState(state_dict, bind_to=self)

    def __str__(self):
        string = f"{self.id} - {self.name}"
        if not self.state.reachable:
            status_string = " (unreachable)"
        else:
            status_string = " (on)" if self.state.is_on else " (off)"
        return string + status_string

    def toggle_on(self):
        self.state.is_on = not self.state.is_on

    def set_on(self):
        self.state.is_on = True

    def set_off(self):
        self.state.is_on = False

    # Provide values r, g, b between 0 and 1
    def set_color(self, hue, saturation):
        self.state.color = hue, saturation

    # Brightness should be between 0 and 254, but also accept between 0 and 1
    def set_brightness(self, brightness):
        self.state.brightness = brightness

    # Private methods

    # This is the reactive binding that gets called when a state value changes
    def set_state(self, state):
        try:
            state_url = self.light_url + "state/"
            response = re.put(state_url, json=state)
            status_code = response.status_code
            if status_code >= 300:
                raise FailedToSetState
            self.state = LightState(state, bind_to=self)
        except FailedToSetState as e:
            print(e.msg)
