class HueGroup:
    def __init__(self, id, name, lights):
        self.id = id
        self.name = name
        self.lights = lights

    def __str__(self):
        num_lights = len(self.lights)
        result = f"Group({self.id}) - {self.name} - {num_lights} lights"
        for light in self.lights:
            result = result + "\n" + light.__str__()
        return result
