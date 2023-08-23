""" DataGenerator

reference:
## prevent create __pycache__ file
https://stackoverflow.com/questions/50752302/python3-pycache-generating-even-if-pythondontwritebytecode-1
## Update view layer
https://blender.stackexchange.com/questions/140789/what-is-the-replacement-for-scene-update
"""

## Add SDG related python files path to system path
import sys
import os
module_path = os.path.dirname(os.path.abspath(__file__))
sys_path_list = []
for p in sys.path:
    sys_path_list.append(p)
if module_path not in sys_path_list:
    sys.path.append(module_path)
# Prevent to create __pycache__ file
sys.dont_write_bytecode = True

import bpy
from SDG_000_Initializer import Initializer
from SDG_010_BackgroundObjectPlacementRandomizer import BackgroundObjectPlacementRandomizer
from SDG_020_ForegroundObjectPlacementRandomizer import ForegroundObjectPlacementRandomizer
from SDG_030_OccluderPlacementRandomizer import OccluderPlacementRandomizer
from SDG_040_ObjectScaleRandomizer import ObjectScaleRandomizer
from SDG_050_TextureRandomizer import TextureRandomizer
from SDG_060_RotationRandomizer import RotationRandomizer
from SDG_070_UnifiedRotationRandomizer import UnifiedRotationRandomizer
from SDG_080_LightRandomizer import LightRandomizer
from SDG_090_CameraRandomizer import CameraRandomizer
from SDG_100_YOLOLabeler_IDMask import YOLOLabeler
from SDG_200_SDGParameter import SDGParameter

class DataGenerator:
    """

    Methods
    -------
    gen_one_data(): 

    References
    ----------


    """
    
    def gen_one_data(self):
        """ 
        """ 
        # SDG component_initialize
        initializer = Initializer()
        parameter = SDGParameter()
        initializer.init()
        background_object_placement_randomizer = BackgroundObjectPlacementRandomizer()
        foreground_object_placement_randomizer = ForegroundObjectPlacementRandomizer()
        occluder_placement_randomizer = OccluderPlacementRandomizer()
        object_scale_randomizer = ObjectScaleRandomizer()
        texture_randomizer = TextureRandomizer()
        rotation_randomizer = RotationRandomizer()
        unified_rotation_randomizer = UnifiedRotationRandomizer()
        light_randomizer = LightRandomizer()
        camera_randomizer = CameraRandomizer()
        yolo_labeler = YOLOLabeler()

        print("Component Initialize Completed!!!")

        # Passing params
        background_object_placement_randomizer.background_poisson_disk_sampling_radius = parameter.background_poisson_disk_sampling_radius
        background_object_placement_randomizer.asset_background_object_folder_path = parameter.asset_background_object_folder_path
        foreground_object_placement_randomizer.num_foreground_object_in_scene_range = parameter.num_foreground_object_in_scene_range
        foreground_object_placement_randomizer.foreground_area = parameter.foreground_area
        foreground_object_placement_randomizer.foreground_poisson_disk_sampling_radius = parameter.foreground_poisson_disk_sampling_radius
        foreground_object_placement_randomizer.asset_foreground_object_folder_path = parameter.asset_foreground_object_folder_path
        occluder_placement_randomizer.num_occluder_in_scene_range = parameter.num_occluder_in_scene_range
        occluder_placement_randomizer.occluder_area = parameter.occluder_area
        occluder_placement_randomizer.occluder_poisson_disk_sampling_radius = parameter.occluder_poisson_disk_sampling_radius
        occluder_placement_randomizer.asset_occluder_folder_path = parameter.asset_occluder_folder_path
        object_scale_randomizer.bg_obj_scale_ratio_range = parameter.bg_obj_scale_ratio_range
        object_scale_randomizer.fg_obj_scale_ratio_range = parameter.fg_obj_scale_ratio_range
        object_scale_randomizer.occluder_scale_ratio_range = parameter.occluder_scale_ratio_range
        texture_randomizer.asset_ambientCGMaterial_folder_path = parameter.asset_ambientCGMaterial_folder_path
        light_randomizer.asset_hdri_lighting_folder_path = parameter.asset_hdri_lighting_folder_path
        light_randomizer.hdri_lighting_strength_range = parameter.hdri_lighting_strength_range
        camera_randomizer.img_resolution_x = parameter.img_resolution_x
        camera_randomizer.img_resolution_y = parameter.img_resolution_y
        camera_randomizer.max_samples = parameter.max_samples
        camera_randomizer.chromatic_aberration_probability = parameter.chromatic_aberration_probability
        camera_randomizer.chromatic_aberration_value_range = parameter.chromatic_aberration_value_range
        camera_randomizer.blur_probability = parameter.blur_probability
        camera_randomizer.blur_value_range = parameter.blur_value_range
        camera_randomizer.motion_blur_probability = parameter.motion_blur_probability
        camera_randomizer.motion_blur_value_range = parameter.motion_blur_value_range
        camera_randomizer.exposure_probability = parameter.exposure_probability
        camera_randomizer.exposure_value_range = parameter.exposure_value_range
        camera_randomizer.noise_probability = parameter.noise_probability
        camera_randomizer.noise_value_range = parameter.noise_value_range
        camera_randomizer.white_balance_probability = parameter.white_balance_probability
        camera_randomizer.white_balance_value_range = parameter.white_balance_value_range
        camera_randomizer.brightness_probability = parameter.brightness_probability
        camera_randomizer.brightness_value_range = parameter.brightness_value_range
        camera_randomizer.contrast_probability = parameter.contrast_probability
        camera_randomizer.contrast_value_range = parameter.contrast_value_range
        camera_randomizer.hue_probability = parameter.hue_probability
        camera_randomizer.hue_value_range = parameter.hue_value_range
        camera_randomizer.saturation_probability = parameter.saturation_probability
        camera_randomizer.saturation_value_range = parameter.saturation_value_range
        yolo_labeler.output_img_path = parameter.output_img_path
        yolo_labeler.output_label_path = parameter.output_label_path

        # Main data generate flow
        background_object_placement_randomizer.background_object_placement_randomize()
        foreground_object_placement_randomizer.foreground_object_placement_randomize()
        occluder_placement_randomizer.occluder_placement_randomize()
        object_scale_randomizer.object_scale_randomize()
        texture_randomizer.texture_randomize()
        rotation_randomizer.rotation_randomize()
        unified_rotation_randomizer.unified_rotation_randomize()
        light_randomizer.light_randomize()
        camera_randomizer.camera_randomize()
        bpy.data.scenes["Scene"].view_layers.update()# Update view layer
        yolo_labeler.get_and_save_yolo_label()

        print("One Data Generating Cylce Completed!!!")
        sys.exit()

if __name__ == '__main__':
    datagen = DataGenerator()
    datagen.gen_one_data()

