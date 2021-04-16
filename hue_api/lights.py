import colorsys
import requests as re

from hue_api.exceptions import FailedToGetState, FailedToSetState
from hue_api.state import LightState

class HueLight:
    """Individually controllable Hue Light

    Raises:
        FailedToSetState: When `self.set_state` fails, usually due to a bad parameter that the Hue API doesn't support.

    Attributes
    
    - `id` (`int`): Light ID
    - `name` (`str`): Light's name
    - `light_url` (`str`): The url that corresponds to the light. Of the form `<bridge_url>/<light.id>`
    - `state` (`LightState`): The reactive light state. This shouldn't be used directly.
    """

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
        """
        Toggle the on/off state of the light
        """
        self.state.is_on = not self.state.is_on

    def set_on(self):
        """
        Set the light state to ON
        """
        self.state.is_on = True

    def set_off(self):
        self.state.is_on = False

    def set_color(self, hue, saturation):
        """
        Set hue and saturation for a light

        Args:
            hue (int): Should be a value [0, 2^16)
            saturation (int): Should be a value [0, 256)
        """
        self.state.color = hue, saturation

    def set_brightness(self, brightness):
        """
        Set brightness for a light

        Args:
            brightness (int): Should be a value [0, 256)
        """
        self.state.brightness = brightness

    # Private methods

    # This is the reactive binding that gets called when a state value changes
    def set_state(self, state):
        """
        Set a new state for the light. This is an internal method and uses the HueState object.
        Don't use this directly.
        """
        try:
            state_url = self.light_url + "state/"
            response = re.put(state_url, json=state)
            status_code = response.status_code
            if status_code >= 300:
                raise FailedToSetState
            self.state = LightState(state, bind_to=self)
        except FailedToSetState as e:
            print(e.msg)
