class FailedToSetState(Exception):
    msg = "There was an error updating state"

class FailedToGetState(Exception):
    msg = "Failed to fetch state from api"

class UninitializedException(Exception):
    msg = "Hue API has not been initialized yet"

class ButtonNotPressedException(Exception):
    msg = "Link button was not pressed"

class DevicetypeException(Exception):
    msg = "Invalid devicetype"
