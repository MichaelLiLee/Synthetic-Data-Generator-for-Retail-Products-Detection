""" UnifiedRotationRandomizer

This Randomizer assigns a random rotation to all foreground (grocery) objects.
The difference between this and RotationRandomizer is that here, the same rotation is applied to all target objects.

"""

import bpy 
import math
import random
from mathutils import Euler

class UnifiedRotationRandomizer:
    def __init__(self):
        self.__collections_for_unified_rotation_randomize = [bpy.data.collections["ForegroundObjectCollection"]]

    def unified_rotation_randomize(self):
        """ Applies a random unified rotation to all objects in collections
        """ 
        for collection in self.__collections_for_unified_rotation_randomize:
            random_rot = (random.random() * 2 * math.pi, random.random() * 2 * math.pi, random.random() * 2 * math.pi)
            for obj_to_unified_rotate in collection.objects:
               obj_to_unified_rotate.rotation_euler = Euler(random_rot, 'XYZ')
        
        print("Unified Rotation Randomize COMPLERED !!!")
    
if __name__ == '__main__':
    randomizer = UnifiedRotationRandomizer()
    randomizer.unified_rotation_randomize()