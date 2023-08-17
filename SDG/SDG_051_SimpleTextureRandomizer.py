import bpy
import os
from glob import glob
import random
import sys

class SimpleTextureRandomizer:
    """
    A randomizer class which randomly select different image textures from Freiburg Groceries dataset and apply it to the surface of the objects.

    Configure the surface textures of objects placed in the virtual scene. The surface textures are derived from 5000 types of image textures.
    Randomly select a subset of these materials and apply them to the surfaces of the objects.

    Attributes
    ----------
    asset_img_texture_path (str): The path to the downloaded Freiburg Groceries dataset image textures.
    __collections_need_assign_texture (list): List of the blender collections which need to apply image texture.
    __objects_need_assign_texture (list): A list of the objects which need to apply image texture.
    __mat (bpy.data.materials): temporary storage of a blender material.

    Methods
    -------
    __create_new_material_and_shader_nodes(): Create blender material shader node group.
    __add_empty_material_to_object(): Add empty material to objects.
    texture_randomize(): Randomly apply image textures to objects.

    References
    ----------
    https://blender.stackexchange.com/questions/23436/control-cycles-eevee-material-nodes-and-material-properties-using-python
    https://blender.stackexchange.com/questions/240278/how-to-access-shader-node-via-python-script
 
    """ 


    def __init__(self ,asset_img_texture_path = "C:/Users/user/Documents/project/synthDet/Asset/image_texture"):
        self.asset_img_texture_path = asset_img_texture_path
        self.__collections_need_assign_texture = [bpy.data.collections["OccluderCollection"],
                                                bpy.data.collections["BackgroundObjectCollection"]]
        self.__objects_need_assign_texture = []
        self.__mat = None


    def __create_new_material_and_shader_nodes(self):
        """Create blender material shader node group.""" 
        # Create new empty material
        self.__mat = bpy.data.materials.new(name="SynthDetMaterial")

        # Get the nodes
        self.__mat.use_nodes = True
        nodes = self.__mat.node_tree.nodes

        # BSDF node reference
        node_PrincipledBSDF =  nodes.get("Principled BSDF")

        # Add new nodes
        node_HueSaturationValue = nodes.new("ShaderNodeHueSaturation")
        node_ImageTexture = nodes.new("ShaderNodeTexImage")
        node_Mapping = nodes.new("ShaderNodeMapping")
        node_TextureCoordinate = nodes.new("ShaderNodeTexCoord")

        node_HueSaturationValue.location = (-200, 200)
        node_ImageTexture.location = (-600,200)
        node_Mapping.location = (-850, 200)
        node_TextureCoordinate.location = (-1100,200)

        # Link nodes
        links = self.__mat.node_tree.links
        links.new(node_TextureCoordinate.outputs["UV"], node_Mapping.inputs["Vector"])
        links.new(node_Mapping.outputs["Vector"], node_ImageTexture.inputs["Vector"])
        links.new(node_ImageTexture.outputs["Color"], node_HueSaturationValue.inputs["Color"])
        links.new(node_HueSaturationValue.outputs["Color"], node_PrincipledBSDF.inputs["Base Color"])


    def __add_empty_material_to_object(self):
        """Add empty material to objects."""    
        #　Add empty material to BG & OCC objects
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
        """Randomly apply image textures to objects."""
         # Create new empty material and shader nodes
        self.__create_new_material_and_shader_nodes()

        # Add empty material to BG & OCC objects
        self.__add_empty_material_to_object()

        # Get img texture asset path 
        img_texture_path_list = glob(os.path.join(self.asset_img_texture_path, "*.jpg")) + \
                                glob(os.path.join(self.asset_img_texture_path, "*.png"))

        num_objects_need_assign_texture = len(self.__objects_need_assign_texture)
        num_img_texture = len(img_texture_path_list)

        # Check img textures number is bigger than BG & OCC objects number
        if num_img_texture < num_objects_need_assign_texture:
            print('Warning!!! num_img_texture:{} must bigger than objects_need_assign_texture:{}'.\
                format(num_img_texture, num_objects_need_assign_texture))
            input("Press Enter to continues...")
            sys.exit()
        
        # Randomly select a texture, then add texture to BG & OCC objects material
        img_texture_list_selected = random.sample(img_texture_path_list, num_objects_need_assign_texture)

        for i in range(num_objects_need_assign_texture):
            assign_image = bpy.data.images.load(img_texture_list_selected[i])
            self.__objects_need_assign_texture[i].material_slots[0].material.node_tree.nodes["Image Texture"].image = assign_image

        print('Simple Texture Randomize COMPLERED !!!')


if __name__ == '__main__':
    randomizer = SimpleTextureRandomizer()
    randomizer.texture_randomize()