class FailedToSetState(Exception):
    """
    There was an error updating state, usually because a paramter passed to the bridge was malformed or of the wrong type.
    """
    msg = "There was an error updating state"

class FailedToGetState(Exception):
    """
    Failed to fetch light state from the API
    """
    msg = "Failed to fetch state from api"

class UninitializedException(Exception):
    """
    Tried to access the hue bridge before the user (API Key) has been obtained.
    """
    msg = "Hue API has not been initialized yet"

class ButtonNotPressedException(Exception):
    """
    Tried to `create_new_user` without pressing the button on the Hue Bridge
    """
    msg = "Link button was not pressed"

class DevicetypeException(Exception):
    """
    The device at the provided IP address/URL can't be controlled via this API
    """
    msg = "Invalid devicetype"
