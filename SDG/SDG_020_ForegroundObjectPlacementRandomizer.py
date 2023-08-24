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
    """
    A randomizer class which randomly spawns foreground objects.

    The foreground generation process of the blender scene involves selecting a subset from a pool of 63 retail items 3D assets.
    These chosen 3D assets are placed randomly within the region above the background objects.
    The placement positions of the foreground objects and their distances from each other are determined through 
    Poisson distribution sampling within the specified spatial area.

    Attributes
    ----------
    num_foreground_object_in_scene_range (dict of str: int): The distribution of the number of retail items within the blender scene.
    __num_foreground_object_in_scene (int): The number of retail items within the blender scene.
    foreground_area (list of float): Spatial distribution area of foreground objects.
    foreground_poisson_disk_sampling_radius (float): Foreground objects separation distance.
    asset_foreground_object_folder_path (str): The path to foreground object assets.
    __foreground_object_collection (bpy.types.Collection): The blender collection data-block of foreground objects.
    __n_particle (int): Number of generated particles of the poisson disks sampling.
    __particle_coordinates (numpy.ndarray): Coordinates of the poisson disks sampling.

    Methods
    -------
    __error_check(): Check assigned background object assets folder path isn't empty.
    __load_object(): Load asset from other blendfile to the current blendfile.
    __posson_disc_sampling(): Using poisson disk sampling algorithm to generate the sampling.
    __import_foreground_object_asset(): Import a number of __n_particle foreground objects into current blender scene.
    foreground_object_placement_randomize(): Generate foreground.

    """

    def __init__(self,
                 num_foreground_object_in_scene_range = {"min": 8 , "max": 20},
                 foreground_area = [2, 1.5, 0.5],
                 foreground_poisson_disk_sampling_radius = 0.3,
                 asset_foreground_object_folder_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/Assets/foreground_object"
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
        """Check assigned background object assets folder path isn't empty.

        Args:
            asset_path_list (list of str): list of the path to background object assets.

        """ 
        num_asset_in_folder = len(asset_path_list)
        if num_asset_in_folder < 1:
            print(f'ERROR!!! can not find any foreground asset in {self.asset_foreground_object_folder_path}')
            input("Press Enter to continue...")
            sys.exit()
    

    def __load_object(self,filepath):
        """Load asset from other blendfile to the current blendfile.

        Args:
            filepath (str): The path to background object assets.

        References
        ----------
        https://studio.blender.org/training/scripting-for-artists/5eabe54d521eafd0953f6d45/
        https://docs.blender.org/api/current/bpy.types.BlendDataLibraries.html
        https://blender.stackexchange.com/questions/17876/import-object-without-bpy-ops-wm-link-append/33998#33998 
        https://blender.stackexchange.com/questions/34540/how-to-link-append-a-data-block-using-the-python-api?noredirect=1&lq=1
        """ 
        ## Append object from .blend file
        with bpy.data.libraries.load(filepath, link = False,assets_only = True) as (data_from, data_to):
            data_to.objects = data_from.objects
        ## Link object to current scene
        for obj in data_to.objects:
            if obj is not None:
                self.__foreground_object_collection.objects.link(obj)


    def __posson_disc_sampling(self):
        """Generate the sampling with a spatially variable sampling radius."""
        # It seem like function poisson_disc_sampling sometimes will break (mtbf:2000-3000 cycle), when it break , return a empty list[]
        # add condition check len(self.__particle_coordinates) must >= 1
        while self.__n_particle == None or self.__n_particle == 0:
            self.__particle_coordinates = poissonDiscSampling.poisson_disc_sampling(radius = self.foreground_poisson_disk_sampling_radius,
                                                                            sample_domain_size = self.__foreground_domain_size,
                                                                            sample_rejection_threshold = 30)
            self.__n_particle = len(self.__particle_coordinates)
            
        loc_offset = np.array([self.__foreground_domain_size[0]/2,self.__foreground_domain_size[1]/2,-0.5])
        self.__particle_coordinates -= loc_offset


    def __import_foreground_object_asset(self):
        """Import a number of __n_particle foreground objects into current blender scene."""  
        # Check n_particle must bigger than num_foreground_object_in_scene
        if self.__n_particle < self.__num_foreground_object_in_scene:
            print('Warning!!! nParticle:{} must bigger than fg_obj_in_scene_num:{}'.format(self.__n_particle,self.__num_foreground_object_in_scene))
            input("Press Enter to continue...") 
            sys.exit()
        
        # Get foreground object asset path
        foreground_object_path_list = glob.glob(os.path.join(self.asset_foreground_object_folder_path, "*.blend"))
        self.__error_check(asset_path_list = foreground_object_path_list)
        num_fg_obj = len(foreground_object_path_list)
        print("num fg obj in folder: {}".format(num_fg_obj))

        # Check num_foreground_object_in_scene is bigger than num_fg_obj
        if self.__num_foreground_object_in_scene >= num_fg_obj:
            # Loop importforeground object
            num_loop = self.__num_foreground_object_in_scene // num_fg_obj
            num_remain = self.__num_foreground_object_in_scene % num_fg_obj

            for i in range(num_loop):
                for fg_obj_path in foreground_object_path_list:
                    self.__load_object(filepath = fg_obj_path)

            if num_remain != 0:
                for i in range(num_remain):
                    self.__load_object(filepath = foreground_object_path_list[i])
        else:
            # Randomly select n(n=num_foreground_object_in_scene) fg_obj from foreground_object_path_list, then import to scene
            foreground_object_path_list_selected = random.sample(foreground_object_path_list, self.__num_foreground_object_in_scene)
            for fg_obj_path in foreground_object_path_list_selected:
                self.__load_object(filepath = fg_obj_path)
    

    def foreground_object_placement_randomize(self):
        """Generate foreground.

        References
        [1]https://stackoverflow.com/questions/14262654/numpy-get-random-set-of-rows-from-2d-array
        """
        self.__num_foreground_object_in_scene = random.randint(self.num_foreground_object_in_scene_range["min"], self.num_foreground_object_in_scene_range["max"])

        # PoissonDiskSampling
        self.__posson_disc_sampling()

        # Import background object asset
        self.__import_foreground_object_asset()

        # Randomly select n(n=num_foreground_object_in_scene) location from __particle_coordinates [1]
        selected_indices = np.random.choice(self.__particle_coordinates.shape[0], 
                                            size = self.__num_foreground_object_in_scene, 
                                            replace = False)
        fg_location = self.__particle_coordinates[selected_indices]
        print("fg_num: {} ".format(len(fg_location)))
        print("fg_location:\n {} ".format(fg_location))

        # Move all foregeound objects to fg_location
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