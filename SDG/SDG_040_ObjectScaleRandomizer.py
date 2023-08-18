import bpy
import random


class ObjectScaleRandomizer:
    """
    A randomizer class which randomizes the scale of the background, foreground and occluder objects in the scene.

    Attributes
    ----------
    bg_obj_scale_ratio_range (dict): The distribution of the scale ratio of background objects within the blender scene.
    fg_obj_scale_ratio_range (dict): The distribution of the scale ratio of foreground objects within the blender scene.
    occluder_scale_ratio_range (dict): The distribution of the scale ratio of occluder objects within the blender scene.
    __background_object_collection (bpy.data.collections): The blender collection data-block of background objects.
    __foreground_object_collection (bpy.data.collections): The blender collection data-block of foreground objects.
    __occluder_collection (bpy.data.collections): The blender collection data-block of occlusion objects.

    Methods
    -------
    __obj_scale_randomize(): Randomizes the scale of the objects in the scene.
    __background_scale_randomize(): Randomizes the scale of the background objects in the scene.
    __foreground_scale_randomize(): Randomizes the scale of the foreground objects in the scene.
    __occluder_scale_randomize(): Randomizes the scale of the occluder objects in the scene.
    object_scale_randomize(): Randomizes the scale of the background, foreground and occluder objects in the scene.

    """ 

    def __init__(self, 
                bg_obj_scale_ratio_range = {"min": 2.5, "max": 2.5},
                fg_obj_scale_ratio_range = {"min": 0.7, "max": 2.2},
                occluder_scale_ratio_range = {"min": 0.5, "max": 1}):

        self.bg_obj_scale_ratio_range = bg_obj_scale_ratio_range
        self.fg_obj_scale_ratio_range = fg_obj_scale_ratio_range
        self.occluder_scale_ratio_range = occluder_scale_ratio_range
        self.__background_object_collection = bpy.data.collections["BackgroundObjectCollection"]
        self.__foreground_object_collection = bpy.data.collections["ForegroundObjectCollection"]
        self.__occluder_collection = bpy.data.collections["OccluderCollection"]


    def __obj_scale_randomize(self, collection, obj_scale_ratio_range):
        """Randomizes the scale of the objects in the scene.

        Args:
            collection (bpy.data.collections): The blender collection data-block of scaled objects.
            obj_scale_ratio_range (dict): The distribution of the scale ratio of objects.

        """ 
        for obj in collection.objects:
            if obj_scale_ratio_range["min"] == obj_scale_ratio_range["max"]:
                scale_ratio = obj_scale_ratio_range["max"]
            else:
                scale_ratio = random.randrange(int(obj_scale_ratio_range["min"]*10),
                                    int(obj_scale_ratio_range["max"]*10), 1)/10
            prev_size = obj.dimensions.xyz
            scale_size = prev_size * scale_ratio
            obj.dimensions.xyz = scale_size[0], scale_size[1], scale_size[2]

        print(f"Object in {collection.name} Scale Randomize COMPLERED!")


    def __background_scale_randomize(self):
        """Randomizes the scale of the background objects in the scene.""" 
        self.__obj_scale_randomize(self.__background_object_collection, self.bg_obj_scale_ratio_range)


    def __foreground_scale_randomize(self):
        """Randomizes the scale of the foreground objects in the scene.""" 
        self.__obj_scale_randomize(self.__foreground_object_collection, self.fg_obj_scale_ratio_range)


    def __occluder_scale_randomize(self):
        """Randomizes the scale of the occluder objects in the scene.""" 
        self.__obj_scale_randomize(self.__occluder_collection, self.occluder_scale_ratio_range)


    def object_scale_randomize(self):
        """Randomizes the scale of the background, foreground and occluder objects in the scene.""" 
        self.__background_scale_randomize()
        self.__foreground_scale_randomize()
        self.__occluder_scale_randomize()

        print(f"Object Scale Randomize COMPLERED !!!")


if __name__ == '__main__':
    randomizer = ObjectScaleRandomizer()
    randomizer.object_scale_randomize()