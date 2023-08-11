"""Looper

references:
https://www.w3resource.com/python-exercises/python-basic-exercise-65.php
"""

## prevent create __pycache__ file
import sys
sys.dont_write_bytecode = True

import subprocess
import os
from SynthDetSDG_200_SynthDetParameter import SynthDetParameter
import collections
import time

class Looper:
    def __init__(self, gen_num =  5000):
        self.__gen_num = gen_num
        self.__gen_num_counter = 0
        self.__remain_gen_num = 0
        self.__start_time = 0
        self.__end_time = 0
        self.__time_seque = collections.deque(maxlen=20)
        self.__time_list = list()
        self.__average_time_consume_per_img = 1
        self.__gen_1k_imgs_eta = None ## format dd:hh:mm:ss
        self.__gen_n_imgs_eta = None ## format dd:hh:mm:ss
        self.__logger = {
            "asset_background_object_folder_path": None,
            "asset_foreground_object_folder_path": None,
            "asset_occluder_folder_path": None,
            "asset_ambientCGMaterial_folder_path": None,
            "asset_hdri_lighting_folder_path": None,
            "output_img_path": None,
            "output_label_path": None,
            "num_foreground_object_in_scene_range": None,
            "num_occluder_in_scene_range": None,
            "max_samples": None,
            "chromatic_aberration_probability": None,
            "blur_probability": None,
            "motion_blur_probability": None,
            "exposure_probability": None,
            "noise_probability": None,
            "white_balance_probability": None,
            "brightness_probability": None,
            "contrast_probability": None,
            "hue_probability": None,
            "saturation_probability": None
        }

    def __create_and_save_logger(self):
        """
        """
        parameter = SynthDetParameter()
        self.__logger["asset_background_object_folder_path"] = parameter.asset_background_object_folder_path
        self.__logger["asset_foreground_object_folder_path"] = parameter.asset_foreground_object_folder_path
        self.__logger["asset_occluder_folder_path"] = parameter.asset_occluder_folder_path
        self.__logger["asset_ambientCGMaterial_folder_path"] = parameter.asset_ambientCGMaterial_folder_path
        self.__logger["asset_hdri_lighting_folder_path"] = parameter.asset_hdri_lighting_folder_path
        self.__logger["output_img_path"] = parameter.output_img_path
        self.__logger["output_label_path"] = parameter.output_label_path
        self.__logger["num_foreground_object_in_scene_range"] = parameter.num_foreground_object_in_scene_range
        self.__logger["num_occluder_in_scene_range"] = parameter.num_occluder_in_scene_range
        self.__logger["max_samples"] = parameter.max_samples
        self.__logger["chromatic_aberration_probability"] = parameter.chromatic_aberration_probability
        self.__logger["blur_probability"] = parameter.blur_probability
        self.__logger["motion_blur_probability"] = parameter.motion_blur_probability
        self.__logger["exposure_probability"] = parameter.exposure_probability
        self.__logger["noise_probability"] = parameter.noise_probability
        self.__logger["white_balance_probability"] = parameter.white_balance_probability
        self.__logger["brightness_probability"] = parameter.brightness_probability
        self.__logger["contrast_probability"] = parameter.contrast_probability
        self.__logger["hue_probability"] = parameter.hue_probability
        self.__logger["saturation_probability"] = parameter.saturation_probability

        ## save to txt
        with open("SynthDet_log.txt",'w') as f:
            for key, value in self.__logger.items():
                f.write('%s:%s\n' % (key, value))

    def __convert_time(self,time):
        """
        """ 
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time
     
        return "d:h:m:s-> %d:%02d:%02d:%02d" % (day, hour, minutes, seconds)

    def ___caculate_gen_imgs_eta(self):
        """ 
        """
        time_consume = self.__end_time - self.__start_time
        self.__time_seque.appendleft(time_consume)
        time_list = list(self.__time_seque)
        self.__average_time_consume_per_img = sum(time_list) / len(time_list)
        
        ## calculate gen_1k_imgs_time_consume
        gen_1k_imgs_time_consume = self.__average_time_consume_per_img * 1000
        self.__gen_1k_imgs_eta = self.__convert_time(time = gen_1k_imgs_time_consume)
        
        ## calculate gen_num imgs time consume
        self.__remain_gen_num = self.__gen_num - self.__gen_num_counter
        gen_n_imgs_time_consume = self.__average_time_consume_per_img * self.__remain_gen_num
        self.__gen_n_imgs_eta = self.__convert_time(time = gen_n_imgs_time_consume)

    def loop(self):
        """ 
        """
        self.__create_and_save_logger()
        ## passing  gen_num param
        parameter = SynthDetParameter()
        self.__gen_num = parameter.gen_num

        while self.__gen_num_counter < self.__gen_num:

            ## log start time
            self.__start_time = time.time()

            ## get blender exe path
            blender_exe_path = parameter.blender_exe_path

            ## get SynthDetSDG_300_DataGenerator.py path
            module_path = os.path.dirname(os.path.abspath(__file__))
            data_generator_path = os.path.join(module_path,"SynthDetSDG_300_DataGenerator.py")

            ## set args
            args = [
                blender_exe_path,
                "--python",
                data_generator_path
                ]

            ## create new process
            subprocess.run(args)

            self.__gen_num_counter += 1
            
            ## log end time
            self.__end_time = time.time()

            self.___caculate_gen_imgs_eta()

            print(f"Generate 1 Image ETA: {int(self.__average_time_consume_per_img)} Seconds")
            print(f"Generate 1k Images ETA: {self.__gen_1k_imgs_eta}")
            print(f"Already Generated {self.__gen_num_counter}/{self.__gen_num} Images")
            print(f"Remain {self.__remain_gen_num} Images Need To Generate, ETA: {self.__gen_n_imgs_eta}")

        print(f"Generate {self.__gen_num} Images COMPLERED !!!")

if __name__ == '__main__':
    looper = Looper()
    looper.loop()