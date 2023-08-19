""" CameraRandomizer

Randomizes post-processing effects on the camera. These include saturation, contrast, and blur.

reference:
https://gist.github.com/andrewbolster/10274979  # random_three_vector
https://www.adamsmith.haus/python/answers/how-to-sample-a-random-number-from-a-probability-distribution-in-python
https://blenderartists.org/t/blackbody-behavior-when-using-with-light-sources/1452214 # white balance node
https://blender.stackexchange.com/questions/5387/how-to-handle-creating-a-node-group-in-a-script
https://blenderartists.org/t/python-add-custom-nodegroup/1205661

Color Temperature (Kelvin) to RGB
https://blender.stackexchange.com/questions/111325/using-python-how-can-i-preset-points-in-shadernode-rgb-curves
https://tannerhelland.com/2012/09/18/convert-temperature-rgb-algorithm-code.html
paper:
"What else can fool deep learning? Addressing color constancy errors on deep neural network performance." ICCV2019.
"When color constancy goes wrong: Correcting improperly white-balanced images." CVPR2019.


Modeling Camera Effects to Improve Visual Learning from Synthetic Data
ChromaticAberration : https://blender.stackexchange.com/questions/168498/is-chromatic-aberration-possible-in-blender
Blur : https://docs.blender.org/manual/en/latest/compositing/types/filter/blur_node.html​
Exposure : https://docs.blender.org/manual/en/latest/compositing/types/color/exposure.html​
Noise: https://blender.stackexchange.com/questions/238692/how-to-add-film-grain-using-the-compositor​
"""

import bpy
from util.RandomThreeVector import random_three_vector
import numpy as np
import random

class CameraRandomizer:
    """ 
     

   c
    ----------
    camera_focal_length (int):
    img_resolution_x (int):
    img_resolution_y (int):
    max_samples (int):
    chromatic_aberration_probability (float):
    chromatic_aberration_value_range (dict of str: float):
    blur_probability ():
    blur_value_range (dict of str: int):
    motion_blur_probability (float):
    motion_blur_value_range (dict of str: ):
    exposure_probability ():
    exposure_value_range (dict of str: ):
    noise_probability ():
    noise_value_range (dict of str: ):
    white_balance_probability (float):
    white_balance_value_range (dict of str: ):
    brightness_probability (float):
    brightness_value_range (dict of str: ):
    contrast_probability (float):
    contrast_value_range (dict of str: ):
    hue_probability ():
    hue_value_range (dict of str: ):
    saturation_probability (float):
    saturation_value_range (dict of str: ):
    __vector_blur_factor ():
    __curve_g_point_list ():
    __curve_b_point_list ():

    Methods
    -------

    References
    ----------

    """
    def __init__(self,
                 camera_focal_length = 35,
                 img_resolution_x = 1728,
                 img_resolution_y = 1152,
                 max_samples = 256,
                 chromatic_aberration_probability = 1,
                 chromatic_aberration_value_range = {"min": 0.1, "max": 1},
                 blur_probability = 1,
                 blur_value_range = {"min": 2, "max": 4},
                 motion_blur_probability = 1,
                 motion_blur_value_range = {"min": 2, "max": 10},
                 exposure_probability = 1,
                 exposure_value_range = {"min": -1.5, "max": 1.5},
                 noise_probability = 1,
                 noise_value_range = {"min": 1.6, "max": 1.8},
                 white_balance_probability = 1,
                 white_balance_value_range = {"min": 3500, "max": 9500},
                 brightness_probability = 1,
                 brightness_value_range = {"min": -5, "max": 5},
                 contrast_probability = 1,
                 contrast_value_range = {"min": -5, "max": 5},
                 hue_probability = 1,
                 hue_value_range = {"min": 0.45, "max": 0.55},
                 saturation_probability = 1,
                 saturation_value_range = {"min": 0.75, "max": 1.25},
                 ):

        self.camera_focal_length = camera_focal_length
        self.img_resolution_x = img_resolution_x
        self.img_resolution_y = img_resolution_y
        self.max_samples = max_samples
        ## Len Effect Augmentation
        self.chromatic_aberration_probability = chromatic_aberration_probability
        self.chromatic_aberration_value_range = chromatic_aberration_value_range
        self.blur_probability = blur_probability
        self.blur_value_range = blur_value_range
        self.motion_blur_probability = motion_blur_probability
        self.motion_blur_value_range = motion_blur_value_range
        ## Sensor Effect Augmentation
        self.exposure_probability = exposure_probability
        self.exposure_value_range = exposure_value_range
        self.noise_probability = noise_probability
        self.noise_value_range = noise_value_range
        ## Post-Processing Effect Augmentation
        self.white_balance_probability = white_balance_probability
        self.white_balance_value_range = white_balance_value_range
        self.brightness_probability = brightness_probability
        self.brightness_value_range = brightness_value_range
        self.contrast_probability = contrast_probability
        self.contrast_value_range = contrast_value_range
        self.hue_probability = hue_probability
        self.hue_value_range = hue_value_range
        self.saturation_probability = saturation_probability
        self.saturation_value_range = saturation_value_range

        self.__vector_blur_factor = 10
        self.__curve_r_point_list = [[0.0, 0.0], 
                                     [0.02500000037252903, 1.0], [0.16249999403953552, 1.0], 
                                     [0.16750000417232513, 0.9696000218391418], [0.17499999701976776, 0.9101999998092651], 
                                     [0.20000000298023224, 0.7644000053405762], [0.22499999403953552, 0.6693000197410583], 
                                     [0.25, 0.6032999753952026], [0.2750000059604645, 0.5551000237464905], 
                                     [0.3125, 0.5037000179290771], [0.375, 0.44929999113082886], 
                                     [0.5, 0.3928000032901764], [0.75, 0.34709998965263367], 
                                     [1.0, 0.3276999890804291]]
        self.__curve_g_point_list = [[0.0, 0.0],
                                     [0.012500000186264515, 0.0], [0.02500000037252903, 0.04010000079870224],
                                     [0.029999999329447746, 0.0860000029206276], [0.03750000149011612, 0.15150000154972076],
                                     [0.05000000074505806, 0.2484000027179718], [0.0625, 0.357699990272522],
                                     [0.07500000298023224, 0.45890000462532043], [0.10000000149011612, 0.6353999972343445],
                                     [0.125, 0.77920001745224], [0.13750000298023224, 0.8403000235557556],
                                     [0.15000000596046448, 0.8952000141143799], [0.1574999988079071, 0.9254000186920166],
                                     [0.16249999403953552, 0.9445000290870667], [0.16750000417232513, 0.9336000084877014],
                                     [0.17499999701976776, 0.8999999761581421], [0.20000000298023224, 0.8138999938964844],
                                     [0.22499999403953552, 0.7541000247001648], [0.25, 0.7106000185012817],
                                     [0.3125, 0.6410999894142151], [0.375, 0.6007000207901001],
                                     [0.5, 0.5565000176429749], [0.75, 0.5188000202178955],
                                     [1.0, 0.5022000074386597]]
        self.__curve_b_point_list = [[0.0, 0.0], 
                                     [0.04749999940395355, 0.0], [0.05249999836087227, 0.015300000086426735], 
                                     [0.0625, 0.06400000303983688], [0.07500000298023224, 0.14830000698566437], 
                                     [0.10000000149011612, 0.3684000074863434], [0.125, 0.6179999709129333], 
                                     [0.15000000596046448, 0.866599977016449], [0.1574999988079071, 0.9383999705314636], 
                                     [0.16249999403953552, 0.9853000044822693], [0.16500000655651093, 1.0], 
                                     [1.0, 1.0]]

    def __set_camera(self):
        """ 
        """
        ## set camera focal length 
        bpy.data.cameras['Camera'].lens = self.camera_focal_length

        ## set img resolution
        bpy.data.scenes['Scene'].render.resolution_x = self.img_resolution_x
        bpy.data.scenes['Scene'].render.resolution_y = self.img_resolution_y

        ## num of samples to render for each pixel
        bpy.data.scenes['Scene'].cycles.samples = self.max_samples

    def __set_curve_point_loction(self, curve_channel, point_list):

        ## add new points
        points_num_need = len(point_list)
        exist_points_num = len(curve_channel.points)
        points_need_add_num = points_num_need - exist_points_num
        for i in range(points_need_add_num):
            curve_channel.points.new(1,1)

        ## set points locations
        for point, location in zip(curve_channel.points, point_list):
            point.location[0] = location[0]
            point.location[1] = location[1]

    def __create_wb_node_group(self):
        """ 
        """
        ## active compositing nodes
        bpy.data.scenes['Scene'].use_nodes = True

        ## check white balance is exist
        for group in bpy.data.node_groups:
            if group.name == "WhiteBalanceNode":
                return

        ## create a group
        wb_group = bpy.data.node_groups.new("WhiteBalanceNode", "CompositorNodeTree")

        ## create group inputs
        group_inputs = wb_group.nodes.new("NodeGroupInput")
        group_inputs.location = (-800, 0)
        wb_group.inputs.new("NodeSocketColor", "Image")
        wb_group.inputs.new("NodeSocketFloat", "ColorTemperature")
        wb_group.inputs["ColorTemperature"].default_value = 6500
        wb_group.inputs["ColorTemperature"].min_value = 2000
        wb_group.inputs["ColorTemperature"].max_value = 40000

        ## create group output
        group_output = wb_group.nodes.new("NodeGroupOutput")
        group_output.location = (600, 200)
        wb_group.outputs.new("NodeSocketColor", "Image")

        ## add new nodes
        node_Math_1 = wb_group.nodes.new("CompositorNodeMath")
        node_Math_1.operation = "DIVIDE"
        node_Math_1.inputs[1].default_value = 40000

        node_Math_2 = wb_group.nodes.new("CompositorNodeMath")
        node_Math_2.operation = "DIVIDE"
        node_Math_2.inputs[0].default_value = 1

        node_RGBCurves_1 = wb_group.nodes.new("CompositorNodeCurveRGB")
        node_RGBCurves_2 = wb_group.nodes.new("CompositorNodeCurveRGB")

        node_Multiply = wb_group.nodes.new("CompositorNodeMixRGB")
        node_Multiply.blend_type = "MULTIPLY"

        ## locate nodes
        node_Math_1.location = (-600,-150)
        node_RGBCurves_1.location = (-400,-150)
        node_Math_2.location = (-100,-300)
        node_Multiply.location = (100,-150)
        node_RGBCurves_2.location = (300,200)

        ## link nodes
        links = wb_group.links
        links.new(group_inputs.outputs["Image"], node_RGBCurves_2.inputs["Image"])
        links.new(group_inputs.outputs["ColorTemperature"], node_Math_1.inputs[0])
        links.new(node_Math_1.outputs[0], node_RGBCurves_1.inputs["Image"])
        links.new(node_RGBCurves_1.outputs["Image"], node_Multiply.inputs[1])
        links.new(node_RGBCurves_1.outputs["Image"], node_Math_2.inputs[1])
        links.new(node_Math_2.outputs[0], node_Multiply.inputs[2])
        links.new(node_Multiply.outputs["Image"], node_RGBCurves_2.inputs["White Level"])
        links.new(node_RGBCurves_2.outputs["Image"], group_output.inputs["Image"])

        ## set node_RGBCurves_1 curve point location
        self.__set_curve_point_loction(node_RGBCurves_1.mapping.curves[0], self.__curve_r_point_list)
        self.__set_curve_point_loction(node_RGBCurves_1.mapping.curves[1], self.__curve_g_point_list)
        self.__set_curve_point_loction(node_RGBCurves_1.mapping.curves[2], self.__curve_b_point_list)

    def __create_compositing_nodes(self):
        """ 
        """ 
        ## active compositing nodes
        bpy.data.scenes['Scene'].use_nodes = True

        ## clear all nodes
        bpy.data.scenes['Scene'].node_tree.nodes.clear()

        ## create camera_sensor_noise_texture
        texture = bpy.data.textures.get("camera_sensor_noise")
        if not texture:
            bpy.data.textures.new("camera_sensor_noise", type="NOISE")
            bpy.data.textures["camera_sensor_noise"].intensity = 1.6 # default value

        ## add new nodes
        node_RenderLayers = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeRLayers")
        node_Lensdist = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeLensdist")
        node_Blur = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeBlur")
        node_VectorBlur = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeVecBlur")
        node_Exposure = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeExposure")
        node_Mix = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeMixRGB")
        node_Mix.blend_type = 'MULTIPLY'
        node_Mix.inputs[0].default_value = 0 # default no mix
        node_Texture = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeTexture")
        node_Texture.texture = bpy.data.textures["camera_sensor_noise"]
        node_WhiteBalance = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeGroup")
        node_WhiteBalance.name = "Wb"
        node_WhiteBalance.node_tree = bpy.data.node_groups["WhiteBalanceNode"]
        node_BrightContrast = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeBrightContrast")
        node_HueSaturationValue = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeHueSat")
        node_Composite = bpy.data.scenes['Scene'].node_tree.nodes.new("CompositorNodeComposite")

        node_RenderLayers.location = (-1000,0)
        node_Lensdist.location = (-700,0)
        node_Blur.location = (-500,0)
        node_VectorBlur.location = (-300,0)
        node_Exposure.location = (-100,0)
        node_Mix.location = (100,0)
        node_Texture.location = (-100,-200)
        node_WhiteBalance.location = (300,0)
        node_BrightContrast.location = (500,0)
        node_HueSaturationValue.location = (700,0)
        node_Composite.location = (900,0)

        ## link nodes
        links = bpy.data.scenes['Scene'].node_tree.links
        links.new(node_RenderLayers.outputs["Image"], node_Lensdist.inputs["Image"])
        links.new(node_Lensdist.outputs["Image"], node_Blur.inputs["Image"])
        links.new(node_Blur.outputs["Image"], node_VectorBlur.inputs["Image"])
        links.new(node_VectorBlur.outputs["Image"], node_Exposure.inputs["Image"])
        links.new(node_Exposure.outputs["Image"], node_Mix.inputs[1])
        links.new(node_Texture.outputs["Color"],  node_Mix.inputs[2])
        links.new(node_Mix.outputs["Image"], node_WhiteBalance.inputs["Image"])
        links.new(node_WhiteBalance.outputs["Image"], node_BrightContrast.inputs["Image"])
        links.new(node_BrightContrast.outputs["Image"], node_HueSaturationValue.inputs["Image"])
        links.new(node_HueSaturationValue.outputs["Image"], node_Composite.inputs["Image"])

        ## enable gpu calculation
        bpy.data.scenes["Scene"].node_tree.use_opencl = True

    def __chromatic_aberration_randomize(self):
        """ 
        """
        default_chromatic_aberration_value = 0
        ## set happen distribution
        chromatic_aberration_happen_distribution = [self.chromatic_aberration_probability, 1 - self.chromatic_aberration_probability]
        ## chromatic_aberration randomize
        chromatic_aberration_value_max = int(self.chromatic_aberration_value_range["max"] * 10)
        chromatic_aberration_value_min = int(self.chromatic_aberration_value_range["min"] * 10)
        random_chromatic_aberration_value = random.randrange(chromatic_aberration_value_min, chromatic_aberration_value_max + 1 ,1)/10
        chromatic_aberration_value = random.choices([random_chromatic_aberration_value, default_chromatic_aberration_value], chromatic_aberration_happen_distribution)
        node_Lensdist = bpy.data.scenes['Scene'].node_tree.nodes["Lens Distortion"]
        node_Lensdist.use_projector = True
        node_Lensdist.inputs['Dispersion'].default_value = chromatic_aberration_value[0]

    def __blur_randomize(self):
        """ 
        """ 
        default_blur_value = 0
        ## set happen distribution
        blur_happen_distribution = [self.blur_probability, 1 - self.blur_probability]
        ## blur randomize
        blur_value_max = int(self.blur_value_range["max"])
        blur_value_min = int(self.blur_value_range["min"])
        random_blur_value = random.randrange(blur_value_min, blur_value_max + 1 ,1)
        blur_value = random.choices([random_blur_value, default_blur_value], blur_happen_distribution)
        node_Blur = bpy.data.scenes['Scene'].node_tree.nodes["Blur"]
        node_Blur.size_x = blur_value[0]
        node_Blur.size_y = blur_value[0]

    def __motion_blur_randomize(self):
        """ 
        """ 
        default_motion_blur_vector = (0,0,0)
        ## set happen distribution
        motion_blur_happen_distribution = [self.motion_blur_probability, 1 - self.motion_blur_probability]
        ## motion blur randomize
        motion_blur_value_max = int(self.motion_blur_value_range["max"])
        motion_blur_value_min = int(self.motion_blur_value_range["min"])
        n = random.randrange(motion_blur_value_min, motion_blur_value_max + 1, 1)
        random_vector = random_three_vector()
        random_motion_blur_vector = (random_vector[0] * n, random_vector[1] * n, random_vector[2] * n)
        motion_blur_vector = random.choices([random_motion_blur_vector, default_motion_blur_vector], motion_blur_happen_distribution)
        node_VectorBlur = bpy.data.scenes['Scene'].node_tree.nodes["Vector Blur"]
        node_VectorBlur.factor = self.__vector_blur_factor
        node_VectorBlur.inputs["Speed"].default_value = motion_blur_vector[0]

    def __exposure_randomize(self):
        """ 
        """ 
        default_exposure_value = 0
        ## set happen distribution
        exposure_happen_distribution = [self.exposure_probability, 1 - self.exposure_probability]
        ## exposure randomize
        exposure_value_max = int(self.exposure_value_range["max"] * 10)
        exposure_value_min = int(self.exposure_value_range["min"] * 10)
        random_exposure_value = random.randrange(exposure_value_min, exposure_value_max + 1 ,1)/10
        exposure_value = random.choices([random_exposure_value, default_exposure_value],exposure_happen_distribution)
        node_Exposure = bpy.data.scenes['Scene'].node_tree.nodes["Exposure"]
        node_Exposure.inputs['Exposure'].default_value = exposure_value[0]

    def __noise_randomize(self):
        """ 
        """
        ## set happen distribution
        noise_happen_distribution = [self.noise_probability, 1 - self.noise_probability]
        ## noise randomize
        noise_value_max = int(self.noise_value_range["max"] * 10)
        noise_value_min = int(self.noise_value_range["min"] * 10)
        random_noise_value = random.randrange(noise_value_min, noise_value_max + 1 ,1)/10
        bpy.data.textures["camera_sensor_noise"].intensity = random_noise_value
        noise_mix_fac_list = [0.25, 0.5, 0.75, 1]
        noise_mix_fac =  random.choice(noise_mix_fac_list)
        noise_mix_value = random.choices([noise_mix_fac,0], noise_happen_distribution)
        node_Mix = bpy.data.scenes["Scene"].node_tree.nodes["Mix"]
        node_Mix.inputs['Fac'].default_value = noise_mix_value[0]

    def __white_balance_randomize(self):
        """ 
        """
        default_white_balance_value = 6500
        ## set happen distribution
        white_balance_happen_distribution = [self.white_balance_probability, 1 - self.white_balance_probability]
        ## white balance randomize
        white_balance_value_max = int(self.white_balance_value_range["max"])
        white_balance_value_min = int(self.white_balance_value_range["min"])
        random_white_balance_value = random.randrange(white_balance_value_min, white_balance_value_max + 1 ,1)
        white_balance_value = random.choices([random_white_balance_value, default_white_balance_value],white_balance_happen_distribution)
        node_WhiteBalance = bpy.data.scenes['Scene'].node_tree.nodes["Wb"]
        node_WhiteBalance.inputs['ColorTemperature'].default_value = white_balance_value[0]

    def __brightness_randomize(self):
        """ 
        """
        default_brightness_value = 0
        ## set happen distribution
        brightness_happen_distribution = [self.brightness_probability, 1 - self.brightness_probability]
        ## brightness randomize
        brightness_value_max = int(self.brightness_value_range["max"])
        brightness_value_min = int(self.brightness_value_range["min"])
        random_brightness_value = random.randrange(brightness_value_min, brightness_value_max + 1 ,1)
        brightness_value = random.choices([random_brightness_value, default_brightness_value],brightness_happen_distribution)
        node_BrightContrast = bpy.data.scenes['Scene'].node_tree.nodes["Bright/Contrast"]
        node_BrightContrast.inputs["Bright"].default_value = brightness_value[0]

    def __contrast_randomize(self):
        """ 
        """ 
        default_contrast_value = 0
        ## set happen distribution
        contrast_happen_distribution = [self.contrast_probability, 1 - self.contrast_probability]
        ## contrast randomize
        contrast_value_max = int(self.contrast_value_range["max"])
        contrast_value_min = int(self.contrast_value_range["min"])
        random_contrast_value = random.randrange(contrast_value_min, contrast_value_max + 1 ,1)
        contrast_value = random.choices([random_contrast_value, default_contrast_value], contrast_happen_distribution)
        node_BrightContrast = bpy.data.scenes['Scene'].node_tree.nodes["Bright/Contrast"]
        node_BrightContrast.inputs["Contrast"].default_value = contrast_value[0]

    def __hue_randomize(self):
        """ 
        """
        default_hue_value = 0.5
        ## set happen distribution
        hue_happen_distribution = [self.hue_probability, 1 - self.hue_probability]
        ## hue randomize
        hue_value_max = int(self.hue_value_range["max"] * 1000)
        hue_value_min = int(self.hue_value_range["min"] * 1000)
        random_hue_value = random.randrange(hue_value_min, hue_value_max + 1 ,1) / 1000
        hue_value = random.choices([random_hue_value, default_hue_value], hue_happen_distribution)
        node_HueSaturationValue = bpy.data.scenes['Scene'].node_tree.nodes["Hue Saturation Value"]
        node_HueSaturationValue.inputs['Hue'].default_value = hue_value[0]

    def __saturation_randomize(self):
        """ 
        """
        default_saturation_value = 1
        ## set happen distribution
        saturation_happen_distribution = [self.saturation_probability, 1 - self.saturation_probability]
        ## saturation randomize
        saturation_value_max = int(self.saturation_value_range["max"] * 1000)
        saturation_value_min = int(self.saturation_value_range["min"] * 1000)
        random_saturation_value = random.randrange(saturation_value_min, saturation_value_max + 1 ,1) / 1000
        saturation_value = random.choices([random_saturation_value, default_saturation_value], saturation_happen_distribution)
        node_HueSaturationValue = bpy.data.scenes['Scene'].node_tree.nodes["Hue Saturation Value"]
        node_HueSaturationValue.inputs['Saturation'].default_value = saturation_value[0]

    def test(self):
        """ 
        """ 
    def camera_randomize(self):
        """ 
        """ 
        self.__set_camera()
        self.__create_wb_node_group()
        self.__create_compositing_nodes()
        self.__chromatic_aberration_randomize()
        self.__blur_randomize()
        self.__motion_blur_randomize()
        self.__exposure_randomize()
        self.__noise_randomize()
        self.__white_balance_randomize()
        self.__brightness_randomize()
        self.__contrast_randomize()
        self.__hue_randomize()
        self.__saturation_randomize()

        print("Camera Randomize COMPLERED !!!")

if __name__ == '__main__':

    randomizer = CameraRandomizer()
    randomizer.camera_randomize() 