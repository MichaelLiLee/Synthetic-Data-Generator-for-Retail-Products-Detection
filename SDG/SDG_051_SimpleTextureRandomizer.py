""" SimpleTextureRandomizer

Randomizes the textures of the background shapes and foreground occluder objects.

"""

'''
reference:
https://blender.stackexchange.com/questions/23436/control-cycles-eevee-material-nodes-and-material-properties-using-python
https://blender.stackexchange.com/questions/240278/how-to-access-shader-node-via-python-script
'''

import bpy
import os
from glob import glob
import random
import sys

class TextureRandomizer:
    def __init__(self ,asset_img_texture_path = "C:/Users/user/Documents/project/synthDet/Asset/image_texture"):
        self.asset_img_texture_path = asset_img_texture_path
        self.__collections_need_assign_texture = [bpy.data.collections["OccluderCollection"],
                                                bpy.data.collections["BackgroundObjectCollection"]]
        self.__objects_need_assign_texture = []
        self.__mat = None

    def __create_new_material_and_shader_nodes(self):
        """ 
        """ 
        ## create new empty_material
        self.__mat = bpy.data.materials.new(name="SynthDetMaterial")
        ## get the nodes
        self.__mat.use_nodes = True
        nodes = self.__mat.node_tree.nodes

        ## BSDF node reference
        node_PrincipledBSDF =  nodes.get("Principled BSDF")

        ## add new nodes
        node_HueSaturationValue = nodes.new("ShaderNodeHueSaturation")
        node_ImageTexture = nodes.new("ShaderNodeTexImage")
        node_Mapping = nodes.new("ShaderNodeMapping")
        node_TextureCoordinate = nodes.new("ShaderNodeTexCoord")

        node_HueSaturationValue.location = (-200, 200)
        node_ImageTexture.location = (-600,200)
        node_Mapping.location = (-850, 200)
        node_TextureCoordinate.location = (-1100,200)

        ## link nodes
        links = self.__mat.node_tree.links
        links.new(node_TextureCoordinate.outputs["UV"], node_Mapping.inputs["Vector"])
        links.new(node_Mapping.outputs["Vector"], node_ImageTexture.inputs["Vector"])
        links.new(node_ImageTexture.outputs["Color"], node_HueSaturationValue.inputs["Color"])
        links.new(node_HueSaturationValue.outputs["Color"], node_PrincipledBSDF.inputs["Base Color"])

    def __add_empty_material_to_object(self):
        """ 
        """    
        ##　add empty_material to BG & OCC objects
        for collection in self.__collections_need_assign_texture:
            for obj in collection.objects:
                self.__objects_need_assign_texture.append(obj)
                new_mat = self.__mat.copy()
                new_mat.name = 'Material' +'_' + obj.name

                if obj.data.materials:
                    obj.data.materials[0] = new_mat
                else:
                    obj.data.materials.append(new_mat)

    def texture_randomize(self):
        """
        """
         ## create new empty_material and shader nodes
        self.__create_new_material_and_shader_nodes()

        ## add empty_material to BG & OCC objects
        self.__add_empty_material_to_object()

        ## get img_texture asset path 
        img_texture_path_list = glob(os.path.join(self.asset_img_texture_path, "*.jpg")) + \
                                glob(os.path.join(self.asset_img_texture_path, "*.png"))

        num_objects_need_assign_texture = len(self.__objects_need_assign_texture)
        num_img_texture = len(img_texture_path_list)

        ## check img_texture number is bigger than BG & OCC objects number
        if num_img_texture < num_objects_need_assign_texture:
            print('Warning!!! num_img_texture:{} must bigger than objects_need_assign_texture:{}'.\
                format(num_img_texture, num_objects_need_assign_texture))
            input("Press Enter to continues...")
            sys.exit()
        
        ## randomly select a texture, then add texture to BG & OCC objects material
        img_texture_list_selected = random.sample(img_texture_path_list, num_objects_need_assign_texture)

        for i in range(num_objects_need_assign_texture):
            assign_image = bpy.data.images.load(img_texture_list_selected[i])
            self.__objects_need_assign_texture[i].material_slots[0].material.node_tree.nodes["Image Texture"].image = assign_image

        print('Simple Texture Randomize COMPLERED !!!')

if __name__ == '__main__':
    randomizer = TextureRandomizer()
    randomizer.texture_randomize()