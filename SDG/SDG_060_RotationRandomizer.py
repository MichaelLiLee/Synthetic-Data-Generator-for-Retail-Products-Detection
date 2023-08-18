import bpy 
import math
import random
from mathutils import Euler

class RotationRandomizer:
    """
    A randomizer class which randomly rotates the background shapes and occluder objects.

    Attributes
    ----------
    __collections_for_rotation_randomize (list): List of the blender collections which need to been rotated.

    Methods
    -------
    rotation_randomize(): Applies random rotation to all objects in background and occluder collections.

    """ 

    def __init__(self):
        self.__collections_for_rotation_randomize = [bpy.data.collections["OccluderCollection"],
                                                   bpy.data.collections['BackgroundObjectCollection']]
    

    def rotation_randomize(self):
        """Applies random rotation to all objects in background and occluder collections.""" 
        for collection in self.__collections_for_rotation_randomize:
            for obj_to_rotate in collection.objects:
                random_rot = (random.random() * 2 * math.pi, random.random() * 2 * math.pi, random.random() * 2 * math.pi)
                obj_to_rotate.rotation_euler = Euler(random_rot, 'XYZ')
             
        print("Rotation Randomize COMPLERED !!!")


if __name__ == '__main__':    
    randomizer = RotationRandomizer()
    randomizer.rotation_randomize()