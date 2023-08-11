""" BackgroundObjectPlacementRandomizer

The background consists of a large number of primitive shapes with randomized positions, rotations, textures, and hue offsets.
The purpose of this background is to act as distraction for the machine learning model. 
This Randomizer has the task of instantiating and positioning these primitive shapes.

"""

import bpy
import numpy as np
from util import poissonDiscSampling
import math
import random
from mathutils import Euler
import os
import glob
import sys

class BackgroundObjectPlacementRandomizer:
    def __init__(self, 
                asset_background_object_folder_path = 'C:/Users/user/Documents/project/synthDet/Asset/background_object',
                background_poisson_disk_sampling_radius = 0.2
                ):
        self.__background_plane_size = [3.2,2.4] #x, y 
        self.background_poisson_disk_sampling_radius = background_poisson_disk_sampling_radius
        self.__background_domain_size = np.array([float(self.__background_plane_size[0]),float(self.__background_plane_size[1])])
        self.asset_background_object_folder_path = asset_background_object_folder_path
        self.__background_object_collection = bpy.data.collections["BackgroundObjectCollection"]
        self.__n_particle = None
        self.__particle_coordinates = None

    def __error_check(self,asset_path_list):
        """
        """
        num_asset_in_folder = len(asset_path_list)
        if num_asset_in_folder < 1:
            print(f'ERROR!!! can not find any background asset in {self.asset_background_object_folder_path}')
            input("Press Enter to continue...")
            sys.exit()

    def __load_object(self,filepath):
        """ Asset Linking

        reference:
        https://studio.blender.org/training/scripting-for-artists/5eabe54d521eafd0953f6d45/
        https://docs.blender.org/api/current/bpy.types.BlendDataLibraries.html
        https://blender.stackexchange.com/questions/17876/import-object-without-bpy-ops-wm-link-append/33998#33998 
        https://blender.stackexchange.com/questions/34540/how-to-link-append-a-data-block-using-the-python-api?noredirect=1&lq=1
        """ 
        ## append object from .blend file
        with bpy.data.libraries.load(filepath, link = False,assets_only = True) as (data_from, data_to):
            data_to.objects = data_from.objects
        ## link object to current scene
        for obj in data_to.objects:
            if obj is not None:
                self.__background_object_collection.objects.link(obj)

    def __posson_disc_sampling(self):
        """
        """
        ## it seem like function poisson_disc_sampling sometimes will break (mtbf:2000-3000 cycle), when it break , return a empty list[]
        ## add condition check len(self.__particle_coordinates) must >= 1
        while self.__n_particle == None or self.__n_particle == 0:
            self.__particle_coordinates = poissonDiscSampling.poisson_disc_sampling(radius = self.background_poisson_disk_sampling_radius,
                                                                                    sample_domain_size = self.__background_domain_size,
                                                                                    sample_rejection_threshold = 30)
            self.__n_particle = len(self.__particle_coordinates)

        loc_offset = np.array([float(self.__background_plane_size[0])/2,float(self.__background_plane_size[1])/2])
        self.__particle_coordinates -= loc_offset

    def __import_background_object_asset(self):
        """
        """   
        ## get background object asset path
        background_object_path_list = glob.glob(os.path.join(self.asset_background_object_folder_path, "*.blend"))
        self.__error_check(asset_path_list = background_object_path_list)
        bg_obj_num = len(background_object_path_list)

        if self.__n_particle >= bg_obj_num:
            ## loop import background object
            loop_num = self.__n_particle // len(background_object_path_list)
            remain_num = self.__n_particle % len(background_object_path_list)

            for i in range(loop_num):
                for bg_obj_path in background_object_path_list:
                    self.__load_object(filepath = bg_obj_path)

            if remain_num != 0:
                for i in range(remain_num):
                    self.__load_object(filepath = background_object_path_list[i])
        else:
            ## randomly import background object
            random_bg_obj_list = random.sample(background_object_path_list, self.__n_particle)
            for bg_obj_path in background_object_path_list:
                    self.__load_object(filepath = bg_obj_path)

    def background_object_placement_randomize(self):
        """
        """  
        ## poissonDiskSampling
        self.__posson_disc_sampling()
        ## import background object asset
        self.__import_background_object_asset()
        ## move all backgeound objects to particleCoordinates
        bg_obj_list = []
        for bg_obj in self.__background_object_collection.objects:
            bg_obj_list.append(bg_obj)

        for i in range(self.__n_particle):
            obj_location = (self.__particle_coordinates[i][0], self.__particle_coordinates[i][1], 0)
            bg_obj_list[i].location = obj_location
        
        print("nParticle: {}".format(self.__n_particle))
        #print("particleCoordinates:\n {} ".format(self.__particle_coordinates))
        print("Background Object Placement Randomize COMPLERED !!!")

if __name__ == '__main__':
    randomizer = BackgroundObjectPlacementRandomizer()
    randomizer.background_object_placement_randomize()
