import bpy
import os
from glob import glob
import random
import math
import sys


class LightRandomizer:
    """ 
    A randomizer class which randomly select a high dynamic range image(HDRI) as scene lighting. The HDRIs are download from Poly Haven.
    This randomizer also randomly set the strength factor for the intensity of the HDRI scene light.

    Attributes
    ----------
    asset_hdri_lighting_folder_path (str): The path to the downloaded Poly Haven HDRIs.
    hdri_lighting_strength_range (dict of str: float): The distribution of the strength factor for the intensity of the HDRI scene light.

    Methods
    -------
    __error_check(): Check assigned HDRI assets folder path isn't empty.
    __create_world_shader_nodes(): Create world shader node group.
    light_randomize(): Randomly apply a HDRI lighting and adjust light intensity.

    References
    ----------
    https://blender.stackexchange.com/questions/209584/using-python-to-add-an-hdri-to-world-node

    """ 

    def __init__(self,
                asset_hdri_lighting_folder_path = "C:/Users/user/Documents/project/Synthetic-Data-Generator-for-Retail-Products-Detection/Assets/HDRI",
                hdri_lighting_strength_range = {"min": 0.1 , "max": 2}
                ):
        self.asset_hdri_lighting_folder_path = asset_hdri_lighting_folder_path
        self.hdri_lighting_strength_range = hdri_lighting_strength_range


    def __error_check(self,asset_path_list):
        """Check assigned HDRI assets folder path isn't empty."""
        num_asset_in_folder = len(asset_path_list)
        if num_asset_in_folder < 1:
            print(f'ERROR!!! can not find any light asset in {self.asset_hdri_lighting_folder_path}')
            input("Press Enter to continue...")
            sys.exit()


    def __create_world_shader_nodes(self):
        """Create world shader node group.""" 
        # Use Nodes
        bpy.data.worlds['World'].use_nodes = True

        # Environment node tree reference
        nodes = bpy.data.worlds['World'].node_tree.nodes

        # Clear all nodes
        nodes.clear()

        # Add new nodes 
        node_WorldOutput = nodes.new("ShaderNodeOutputWorld")
        node_Background = nodes.new("ShaderNodeBackground")
        node_EnvironmentTexture = nodes.new("ShaderNodeTexEnvironment")
        node_Mapping = nodes.new("ShaderNodeMapping")
        node_TextureCoordinate = nodes.new("ShaderNodeTexCoord")

        node_WorldOutput.location = (100, 300)
        node_Background.location = (-100, 300)
        node_EnvironmentTexture.location = (-400, 300)
        node_Mapping.location = (-650, 300)
        node_TextureCoordinate.location = (-900, 300)

        # Link nodes
        links = bpy.data.worlds['World'].node_tree.links
        links.new(node_TextureCoordinate.outputs["Generated"], node_Mapping.inputs["Vector"])
        links.new(node_Mapping.outputs["Vector"], node_EnvironmentTexture.inputs["Vector"])
        links.new(node_EnvironmentTexture.outputs["Color"], node_Background.inputs["Color"])
        links.new(node_Background.outputs["Background"], node_WorldOutput.inputs["Surface"])


    def light_randomize(self):
        """Randomly apply a HDRI lighting and adjust light intensity.""" 
        self.__create_world_shader_nodes()

        # Background node reference
        node_Background = bpy.data.worlds['World'].node_tree.nodes["Background"]
        # EnvironmentTexture node reference
        node_EnvironmentTexture = bpy.data.worlds['World'].node_tree.nodes["Environment Texture"]
        # Mapping node reference
        node_MappingLighting = bpy.data.worlds["World"].node_tree.nodes["Mapping"]

        # Get hdri lighting asset path
        hdri_lighting_path_list = glob(os.path.join(self.asset_hdri_lighting_folder_path, "*.exr"))
        self.__error_check(asset_path_list = hdri_lighting_path_list)

        # Randomly select a hdri lighting, then add hdri lighting to node_EnvironmentTexture
        hdri_lighting_selected = random.sample(hdri_lighting_path_list, 1)
        hdri_lighting = bpy.data.images.load(hdri_lighting_selected[0])
        node_EnvironmentTexture.image = hdri_lighting

        # Randomly set lighting strength
        max = int(self.hdri_lighting_strength_range["max"] * 10)
        min = int(self.hdri_lighting_strength_range["min"] * 10)
        lighting_strength = random.randrange(min, max,1)/10
        node_Background.inputs["Strength"].default_value = lighting_strength

        # Randomly rotate lighting
        random_rot_x = random.uniform(-30/360, 120/360) * 2 * math.pi # -30~+120 degree
        random_rot_y = random.uniform(-30/360, 30/360) * 2 * math.pi # -30~+30 degree
        random_rot_z = random.uniform(0,360/360)  * 2* math.pi # 0~360 degree
        node_MappingLighting.inputs["Rotation"].default_value[0] =  random_rot_x
        node_MappingLighting.inputs["Rotation"].default_value[1] =  random_rot_y
        node_MappingLighting.inputs["Rotation"].default_value[2] =  random_rot_z

        print("Light Randomize COMPLERED !!!")


if __name__ == '__main__':
    randomizer = LightRandomizer()
    randomizer.light_randomize()