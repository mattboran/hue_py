class HueScene:
    """
    This class is useful for interfacing with whole scenes. As of v0.3.0, it isn't complete.

    Attributes

    - `id` (`int`): Scene's ID
    - `name` (`str`): Scene's name
    - `lights` (`[HueLight]`): List of lights belonging to this scene
    """
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
        """
        Internal method used to group scenes by name. This is useful because scenes exist individually by light. 
        So if 5 lights have a scene attached to them, you'll see the same scene 5 times.

        Args:
            scenes ([HueScene]): The list of scenes to group

        Returns:
            dict[str: HueScene]: Scenes grouped by name. You can now iterate through the lights in a scene given its name
        """
        scene_names = set([scene.name for scene in scenes])
        groups = {name: [] for name in scene_names}
        for key in groups:
            filtered_scenes = [scene for scene in scenes if scene.name == key]
            groups[key] += filtered_scenes
        return groups
