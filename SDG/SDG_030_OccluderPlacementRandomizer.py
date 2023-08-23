import bpy
import numpy as np
from util import poissonDiscSampling
import math
import random
from mathutils import Euler
import os
import glob
import sys


class OccluderPlacementRandomizer:
    """
    A randomizer class which randomly spawns occluder objects. 

    The method of generating occlusion objects in the blender scene involves selecting from a set of 3D models containing various simple geometric shapes
    such as cubes and cylinders. These occlusion objects are then randomly placed within the region above the foreground objects. The placement positions of 
    the occlusion objects and their distances from each other are determined through Poisson distribution sampling within the specified spatial area.

    Attributes
    ----------
    num_occluder_in_scene_range (dict of str: int): The distribution of the number of occlusion objects within the blender scene.
    __num_occluder_in_scene (int): The number of occlusion objects within the blender scene.
    occluder_area (list of float): Spatial distribution area of occlusion objects.
    __occluder_domain_size (numpy.ndarray): Spatial distribution area of occlusion objects.
    occluder_poisson_disk_sampling_radius (float): Occlusion objects separation distance.
    asset_occluder_folder_path (str): The path to occlusion object assets.
    __occluder_collection (bpy.types.Collection): The blender collection data-block of occlusion objects.
    __n_particle (int): Number of generated particles of the poisson disks sampling.
    __particle_coordinates (numpy.ndarray): Coordinates of the poisson disks sampling.

    Methods
    -------
    __error_check(): Check assigned occlusion object assets folder path isn't empty.
    __load_object(): Load asset from other blendfile to the current blendfile.
    __posson_disc_sampling(): Using poisson disk sampling algorithm to generate the sampling.
    __import_occluder_asset(): Import a number of __n_particle occlusion objects into current blender scene.
    occluder_placement_randomize(): Generate occlusion.

    """ 

    def __init__(self, 
                num_occluder_in_scene_range = {"min": 5 , "max": 10},
                occluder_area = [1.2, 0.8, 0.4],
                occluder_poisson_disk_sampling_radius = 0.25,
                asset_occluder_folder_path = "C:/Users/user/Documents/project/synthDet/Asset/occluder"
                ):
        self.num_occluder_in_scene_range = num_occluder_in_scene_range
        self.__num_occluder_in_scene = None
        self.occluder_area = occluder_area
        self.__occluder_domain_size = np.array(self.occluder_area)
        self.occluder_poisson_disk_sampling_radius = occluder_poisson_disk_sampling_radius
        self.asset_occluder_folder_path = asset_occluder_folder_path
        self.__occluder_collection = bpy.data.collections["OccluderCollection"]
        self.__n_particle = None
        self.__particle_coordinates = None


    def __error_check(self,asset_path_list):
        """Check assigned background object assets folder path isn't empty.

        Args:
            asset_path_list (list of str): list of the path to background object assets.

        """
        num_asset_in_folder = len(asset_path_list)
        if num_asset_in_folder < 1:
            print(f'ERROR!!! can not find any occluder asset in {self.asset_occluder_folder_path}')
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
        # Append object from .blend file
        with bpy.data.libraries.load(filepath, link = False,assets_only = True) as (data_from, data_to):
            data_to.objects = data_from.objects
        # Link object to current scene
        for obj in data_to.objects:
            if obj is not None:
                self.__occluder_collection.objects.link(obj)


    def __posson_disc_sampling(self):
        """Generate the sampling with a spatially variable sampling radius."""
        # It seem like function poisson_disc_sampling sometimes will break (mtbf:2000-3000 cycle), when it break , return a empty list[]
        # Add condition check len(self.__particle_coordinates) must >= 1
        while self.__n_particle == None or self.__n_particle == 0:
            self.__particle_coordinates = poissonDiscSampling.poisson_disc_sampling(radius = self.occluder_poisson_disk_sampling_radius,
                                                                            sample_domain_size = self.__occluder_domain_size,
                                                                            sample_rejection_threshold = 30)
            self.__n_particle = len(self.__particle_coordinates)

        loc_offset = np.array([self.__occluder_domain_size[0]/2,self.__occluder_domain_size[1]/2,-1.5])
        self.__particle_coordinates -= loc_offset


    def __import_occluder_asset(self):
        """Import a number of __n_particle occlusion objects into current blender scene."""  
        # Check n_particle must bigger than num_occluder_in_scene
        if self.__n_particle < self.__num_occluder_in_scene:
            print('Warning!!! nParticle:{} must bigger than num_occluder_in_scene:{}'.format(self.__n_particle,self.__num_occluder_in_scene))
            input("Press Enter to continue...") 
            sys.exit()
        
        # Get occluder asset path
        occluder_path_list = glob.glob(os.path.join(self.asset_occluder_folder_path, "*.blend"))
        self.__error_check(asset_path_list = occluder_path_list)
        num_occluder = len(occluder_path_list)
        print("num occluder in folder: {}".format(num_occluder))

        # Check num_occluder_in_scene is bigger than num_occluder
        if self.__num_occluder_in_scene >= num_occluder:
            # Loop import occluder
            num_loop = self.__num_occluder_in_scene // num_occluder
            num_remain = self.__num_occluder_in_scene % num_occluder

            for i in range(num_loop):
                for occluder_path in occluder_path_list:
                    self.__load_object(filepath = occluder_path)

            if num_remain != 0:
                for j in range(num_remain):
                    self.__load_object(filepath = occluder_path_list[j])

        else:
            # Randomly select n(n=num_occluder_in_scene) occluder from occluder_path_list, then import to scene
            occluder_path_list_selected = random.sample(occluder_path_list, self.__num_occluder_in_scene)
            for occluder_path in occluder_path_list_selected:
                self.__load_object(filepath = occluder_path)


    def occluder_placement_randomize(self):
        """Generate occlusion.

        References
        [1]https://stackoverflow.com/questions/14262654/numpy-get-random-set-of-rows-from-2d-array
        """
        self.__num_occluder_in_scene = random.randint(self.num_occluder_in_scene_range["min"], self.num_occluder_in_scene_range["max"])
        # PoissonDiskSampling
        self.__posson_disc_sampling()
        # Import occluder asset
        self.__import_occluder_asset()
        # Randomly select n(n=num_occluder_in_scene) location from __particle_coordinates [1]
        selected_indices = np.random.choice(self.__particle_coordinates.shape[0], 
                                            size = self.__num_occluder_in_scene, 
                                            replace = False)
        occluder_location = self.__particle_coordinates[selected_indices]
        print("occluder_num: {} ".format(len(occluder_location)))
        print("occluder_location:\n {} ".format(occluder_location))

        # Move all occluder to occluder_location
        occluder_list = []
        for occluder in self.__occluder_collection.objects:
            occluder_list.append(occluder)

        for k in range(self.__num_occluder_in_scene):
            occluder_location_tomove = (occluder_location[k][0],occluder_location[k][1], occluder_location[k][2])
            occluder_list[k].location = occluder_location_tomove

        print("Occluder Placement Randomize COMPLERED !!!")


if __name__ == '__main__':
    randomizer = OccluderPlacementRandomizer()
    randomizer.occluder_placement_randomize()