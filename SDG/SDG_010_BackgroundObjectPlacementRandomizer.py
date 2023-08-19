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
    """ 
    A randomizer class which generate a background consists of a large number of primitive shapes.

    The background generation process of the blender scene involves selecting from a set of 3D models containing various 
    simple geometric shapes such as cubes and cylinders. These chosen models are randomly placed and filled in the background 
    of the virtual scene to form a background wall.The placement positions of the 3D models and their distances from each other 
    are determined throughPoisson distribution sampling within the specified plane area.

    Attributes
    ----------
    __background_plane_size (list of float): Background plane dimension(x, y).
    background_poisson_disk_sampling_radius (str): Background objects separation distance.
    __background_domain_size (numpy.ndarray): Spatial distribution area of background objects.
    asset_background_object_folder_path (str): The path to background object assets.
    __background_object_collection (bpy.types.Collection): The Collection data-block of background objects.
    __n_particle (int): Number of generated particles of the poisson disks sampling.
    __particle_coordinates (numpy.ndarray): Coordinates of the poisson disks sampling.

    Methods
    -------
    __error_check(): Check assigned background object assets folder path isn't empty.
    __load_object(): Load asset from other blendfile to the current blendfile.
    __posson_disc_sampling(): Using poisson disk sampling algorithm to generate the sampling.
    __import_background_object_asset(): Import a number of __n_particle background objects into current blender scene.
    background_object_placement_randomize(): Generate background.

    """

    def __init__(self, 
                asset_background_object_folder_path = 'C:/Users/user/Documents/project/synthDet/Asset/background_object',
                background_poisson_disk_sampling_radius = 0.2
                ):
        self.__background_plane_size = [3.2,2.4] # x, y 
        self.background_poisson_disk_sampling_radius = background_poisson_disk_sampling_radius
        self.__background_domain_size = np.array([float(self.__background_plane_size[0]),float(self.__background_plane_size[1])])
        self.asset_background_object_folder_path = asset_background_object_folder_path
        self.__background_object_collection = bpy.data.collections["BackgroundObjectCollection"]
        self.__n_particle = None
        self.__particle_coordinates = None


    def __error_check(self,asset_path_list):
        """Check assigned background object assets folder path isn't empty.

        Args:
            asset_path_list (list of str): list of the path to background object assets.
        """
        num_asset_in_folder = len(asset_path_list)
        if num_asset_in_folder < 1:
            print(f'ERROR!!! can not find any background asset in {self.asset_background_object_folder_path}')
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
                self.__background_object_collection.objects.link(obj)


    def __posson_disc_sampling(self):
        """Generate the sampling with a spatially variable sampling radius."""
        # It seem like function poisson_disc_sampling sometimes will break (mtbf:2000-3000 cycle), when it break , return a empty list[]
        # add condition check len(self.__particle_coordinates) must >= 1
        while self.__n_particle == None or self.__n_particle == 0:
            self.__particle_coordinates = poissonDiscSampling.poisson_disc_sampling(radius = self.background_poisson_disk_sampling_radius,
                                                                                    sample_domain_size = self.__background_domain_size,
                                                                                    sample_rejection_threshold = 30)
            self.__n_particle = len(self.__particle_coordinates)

        loc_offset = np.array([float(self.__background_plane_size[0])/2,float(self.__background_plane_size[1])/2])
        self.__particle_coordinates -= loc_offset


    def __import_background_object_asset(self):
        """Import a number of __n_particle background objects into current blender scene."""   
        # Get background object asset path
        background_object_path_list = glob.glob(os.path.join(self.asset_background_object_folder_path, "*.blend"))
        self.__error_check(asset_path_list = background_object_path_list)
        bg_obj_num = len(background_object_path_list)

        if self.__n_particle >= bg_obj_num:
            # Loop import background object
            loop_num = self.__n_particle // len(background_object_path_list)
            remain_num = self.__n_particle % len(background_object_path_list)

            for i in range(loop_num):
                for bg_obj_path in background_object_path_list:
                    self.__load_object(filepath = bg_obj_path)

            if remain_num != 0:
                for i in range(remain_num):
                    self.__load_object(filepath = background_object_path_list[i])
        else:
            # Randomly import background object
            random_bg_obj_list = random.sample(background_object_path_list, self.__n_particle)
            for bg_obj_path in background_object_path_list:
                    self.__load_object(filepath = bg_obj_path)


    def background_object_placement_randomize(self):
        """Generate background """  
        # PoissonDiskSampling
        self.__posson_disc_sampling()

        # Import background object asset
        self.__import_background_object_asset()

        # Move all backgeound objects to particleCoordinates
        bg_obj_list = []
        for bg_obj in self.__background_object_collection.objects:
            bg_obj_list.append(bg_obj)

        for i in range(self.__n_particle):
            obj_location = (self.__particle_coordinates[i][0], self.__particle_coordinates[i][1], 0)
            bg_obj_list[i].location = obj_location
        
        print("nParticle: {}".format(self.__n_particle))
        print("Background Object Placement Randomize COMPLERED !!!")


if __name__ == '__main__':
    randomizer = BackgroundObjectPlacementRandomizer()
    randomizer.background_object_placement_randomize()