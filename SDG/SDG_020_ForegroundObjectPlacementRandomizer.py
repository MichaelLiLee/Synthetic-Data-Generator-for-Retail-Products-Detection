""" ForegroundObjectPlacementRandomizer

This Randomizer instantiates and positions the foreground objects.
These are the grocery objects, for which we generate bounding boxes.

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

class ForegroundObjectPlacementRandomizer:
    def __init__(self,
                 num_foreground_object_in_scene_range = {"min": 8 , "max": 20},
                 foreground_area = [2, 1.5, 0.5],
                 foreground_poisson_disk_sampling_radius = 0.3,
                 asset_foreground_object_folder_path = "C:/Users/user/Documents/project/synthDet/Asset/foreground_object"
                 ):
        self.num_foreground_object_in_scene_range = num_foreground_object_in_scene_range
        self.__num_foreground_object_in_scene = None
        self.foreground_area = foreground_area
        self.__foreground_domain_size = np.array(self.foreground_area)
        self.foreground_poisson_disk_sampling_radius = foreground_poisson_disk_sampling_radius
        self.asset_foreground_object_folder_path = asset_foreground_object_folder_path
        self.__foreground_object_collection = bpy.data.collections["ForegroundObjectCollection"]
        self.__n_particle = None
        self.__particle_coordinates = None

    def __error_check(self,asset_path_list):
        """
        """
        num_asset_in_folder = len(asset_path_list)
        if num_asset_in_folder < 1:
            print(f'ERROR!!! can not find any foreground asset in {self.asset_foreground_object_folder_path}')
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
                self.__foreground_object_collection.objects.link(obj)

    def __posson_disc_sampling(self):
        """
        """
        ## it seem like function poisson_disc_sampling sometimes will break (mtbf:2000-3000 cycle), when it break , return a empty list[]
        ## add condition check len(self.__particle_coordinates) must >= 1
        while self.__n_particle == None or self.__n_particle == 0:
            self.__particle_coordinates = poissonDiscSampling.poisson_disc_sampling(radius = self.foreground_poisson_disk_sampling_radius,
                                                                            sample_domain_size = self.__foreground_domain_size,
                                                                            sample_rejection_threshold = 30)
            self.__n_particle = len(self.__particle_coordinates)
            
        loc_offset = np.array([self.__foreground_domain_size[0]/2,self.__foreground_domain_size[1]/2,-0.5])
        self.__particle_coordinates -= loc_offset

    def __import_foreground_object_asset(self):
        """
        """  
        ## check n_particle must bigger than num_foreground_object_in_scene
        if self.__n_particle < self.__num_foreground_object_in_scene:
            print('Warning!!! nParticle:{} must bigger than fg_obj_in_scene_num:{}'.format(self.__n_particle,self.__num_foreground_object_in_scene))
            input("Press Enter to continue...") 
            sys.exit()
        
        ## get foreground object asset path
        foreground_object_path_list = glob.glob(os.path.join(self.asset_foreground_object_folder_path, "*.blend"))
        self.__error_check(asset_path_list = foreground_object_path_list)
        num_fg_obj = len(foreground_object_path_list)
        print("num fg obj in folder: {}".format(num_fg_obj))

        ## check num_foreground_object_in_scene is bigger than num_fg_obj
        if self.__num_foreground_object_in_scene >= num_fg_obj:
            ## loop importforeground object
            num_loop = self.__num_foreground_object_in_scene // num_fg_obj
            num_remain = self.__num_foreground_object_in_scene % num_fg_obj

            for i in range(num_loop):
                for fg_obj_path in foreground_object_path_list:
                    self.__load_object(filepath = fg_obj_path)

            if num_remain != 0:
                for i in range(num_remain):
                    self.__load_object(filepath = foreground_object_path_list[i])
        else:
            ##randomly select n(n=num_foreground_object_in_scene) fg_obj from foreground_object_path_list, then import to scene
            foreground_object_path_list_selected = random.sample(foreground_object_path_list, self.__num_foreground_object_in_scene)
            for fg_obj_path in foreground_object_path_list_selected:
                self.__load_object(filepath = fg_obj_path)
    
    def foreground_object_placement_randomize(self):
        """
        """
        self.__num_foreground_object_in_scene = random.randint(self.num_foreground_object_in_scene_range["min"], self.num_foreground_object_in_scene_range["max"])
        ## poissonDiskSampling
        self.__posson_disc_sampling()
        ## import background object asset
        self.__import_foreground_object_asset()
        ## randomly select n(n=num_foreground_object_in_scene) location from __particle_coordinates
        '''
        https://stackoverflow.com/questions/14262654/numpy-get-random-set-of-rows-from-2d-array
        '''
        selected_indices = np.random.choice(self.__particle_coordinates.shape[0], 
                                            size = self.__num_foreground_object_in_scene, 
                                            replace = False)
        fg_location = self.__particle_coordinates[selected_indices]
        print("fg_num: {} ".format(len(fg_location)))
        print("fg_location:\n {} ".format(fg_location))

        ## move all foregeound objects to fg_location
        fg_obj_list = []
        for fg_obj in self.__foreground_object_collection.objects:
            fg_obj_list.append(fg_obj)

        for i in range(self.__num_foreground_object_in_scene):
            obj_location = (fg_location[i][0],fg_location[i][1], fg_location[i][2])
            fg_obj_list[i].location = obj_location
        
        print("Foreground Object Placement Randomize COMPLERED !!!")

if __name__ == '__main__':
    randomizer = ForegroundObjectPlacementRandomizer()
    randomizer.foreground_object_placement_randomize()
