class HueScene:
    def __init__(self, id, name, lights):
        self.id = id
        self.name = name
        self.lights = lights

    def __str__(self):
        num_lights = len(self.lights)
        result = f"Scene({self.id}) - {self.name} - {num_lights} lights"
        for light in self.lights:
            result = result + "\n" + light.name
        return result

    @staticmethod
    def group_scenes(scenes):
        scene_names = set([scene.name for scene in scenes])
        groups = {name: [] for name in scene_names}
        for key in groups:
            filtered_scenes = [scene for scene in scenes if scene.name == key]
            groups[key] += filtered_scenes
        return groups
