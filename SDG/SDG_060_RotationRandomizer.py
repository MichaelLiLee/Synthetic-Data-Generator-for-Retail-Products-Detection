""" RotationRandomizer

The background shapes, foreground occluder objects, 
 are rotated randomly using this Randomizer.

"""
import bpy 
import math
import random
from mathutils import Euler

class RotationRandomizer:
    def __init__(self):
        self.__collections_for_rotation_randomize = [bpy.data.collections["OccluderCollection"],
                                                   bpy.data.collections['BackgroundObjectCollection']]
    
    def rotation_randomize(self):
        """ Applies a random rotation to an object in collections
        """ 
        for collection in self.__collections_for_rotation_randomize:
            for obj_to_rotate in collection.objects:
                random_rot = (random.random() * 2 * math.pi, random.random() * 2 * math.pi, random.random() * 2 * math.pi)
                obj_to_rotate.rotation_euler = Euler(random_rot, 'XYZ')
             
        print("Rotation Randomize COMPLERED !!!")

if __name__ == '__main__':    
    randomizer = RotationRandomizer()
    randomizer.rotation_randomize()