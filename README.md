# hue_api

[![Build Status](https://travis-ci.org/mattboran/hue_py.svg?branch=master)](https://travis-ci.org/mattboran/hue_py)

This is a simple Python API client for Philips Hue lights.
 
 ## First time Setup
To use this api client for the first time, use:
```
from hue_api import HueApi
api = HueApi()
api.create_new_user(bridge_ip_address)
```
Where the bridge IP address is the addres on the local network of your Philips Hue bridge. For this to succeed, you must first press the link button on the bridge.

The response will be saved to the module's install directory, and you can subsequently call
`api.load_existing()` to access that saved user and IP address the next time you instantiate a `HueApi` object.

## Lights API
This client provides functionality to control lights currently linked to the hue bridge. Calling `api.fetch_lights()` populates an array of `HueLight` objects stored in `api.lights`.

You can then call `api.list_lights()` to get a list of the lights available on the network.

See [documentation](http://hue-py-docs.s3-website-us-east-1.amazonaws.com/) for details on what controls are available.
