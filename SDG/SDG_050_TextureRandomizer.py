import bpy 
import os 
import random
import sys

class TextureRandomizer:
    """
    A randomizer class which randomly select different PBR material and apply it to the surface of the objects.

    Configure the surface textures of objects placed in the blender scene. The surface textures are derived from 1369 types of PBR materials.
    Randomly select a subset of these materials and apply them to the surfaces of the objects.

    Attributes
    ----------
    asset_ambientCGMaterial_folder_path (str): The path to the downloaded ambientCG PBR materials.
    __collections_need_assign_material (list): List of the blender collections which need to apply material.
    __objects_need_assign_material (list): A list of the objects which need to apply material.
    __asset_base_image_path_list (list): All color map img paths from asset_ambientCGMaterial_folder_path.
    __randomly_selected_base_image_path_list (list): A list of randomly selected color map img paths.

    Methods
    -------
     __get_all_material_image_paths(): Get all color map image paths.
     __get_objects_need_assign_material(): Get all objects which need assign material.
     __randomly_select_materials(): Randomly select material.
     __create_and_assign_material(): Create blender material shader node group, then import PBR texture maps.
     texture_randomize(): Randomly apply materials to objects.

    References
    ----------
    https://dlr-rm.github.io/BlenderProc/blenderproc.python.loader.CCMaterialLoader.html#blenderproc.python.loader.CCMaterialLoader.CCMaterialLoader
    https://dlr-rm.github.io/BlenderProc/blenderproc.api.material.html#module-blenderproc.material 
    https://github.com/DLR-RM/BlenderProc/blob/main/blenderproc/python/loader/CCMaterialLoader.py
    https://github.com/DLR-RM/BlenderProc/blob/main/blenderproc/python/material/MaterialLoaderUtility.py

    """

    def __init__(self, asset_ambientCGMaterial_folder_path = "C:/Users/user/Documents/project/synthDet/Asset/blenderproc_asset/cc_texture"):       
        
        self.asset_ambientCGMaterial_folder_path = asset_ambientCGMaterial_folder_path
        self.__collections_need_assign_material = [bpy.data.collections["OccluderCollection"], bpy.data.collections["BackgroundObjectCollection"]]
        self.__objects_need_assign_material = list()
        self.__asset_base_image_path_list = list()
        self.__randomly_selected_base_image_path_list = list()


    def __get_all_material_image_paths(self):
        """Get all color map image paths.""" 
        folder_path = self.asset_ambientCGMaterial_folder_path

        # Get all base_image path from self.asset_ambientCGMaterial_folder_path
        for asset in os.listdir(folder_path):
            asset_path = os.path.join(folder_path, asset)
            if os.path.isdir(asset_path):
                base_image_path = os.path.join(asset_path, f"{asset}_2K_Color.jpg")
                if os.path.exists(base_image_path):
                    self.__asset_base_image_path_list.append(base_image_path)
    

    def __get_objects_need_assign_material(self):
        """Get all objects which need assign material.""" 
        for collection in self.__collections_need_assign_material:
            for obj in collection.objects:
                self.__objects_need_assign_material.append(obj)


    def __randomly_select_materials(self):
        """Randomly select material.""" 
        num_objects_need_assign_material = len(self.__objects_need_assign_material)

        self.__randomly_selected_base_image_path_list =  \
        random.choices(self.__asset_base_image_path_list, k = num_objects_need_assign_material)


    def __create_and_assign_material(self):
        """Create blender material shader node group, then import PBR texture maps.""" 
        num_materials = len(self.__randomly_selected_base_image_path_list)
        num_objs = len(self.__objects_need_assign_material)

        # Check num_materials is equal to num_objs
        if num_materials != num_objs:
            print(f"Warning!!! num_materials: {num_materials} not equal to num_objs: {num_objs}") 
            input("Press Enter to continues...")
            sys.exit()

        for i in range(num_materials):
            current_obj = self.__objects_need_assign_material[i]
            base_image_path = self.__randomly_selected_base_image_path_list[i]
            # Construct all image paths
            ambient_occlusion_image_path =  base_image_path.replace("Color", "AmbientOcclusion")
            metallic_image_path =  base_image_path.replace("Color", "Metalness")
            roughness_image_path =  base_image_path.replace("Color", "Roughness")
            alpha_image_path =  base_image_path.replace("Color", "Opacity")
            normal_image_path =  base_image_path.replace("Color", "NormalGL")
            displacement_image_path =  base_image_path.replace("Color", "Displacement")

            # Create new material
            new_mat_name = 'Material' + '_' + current_obj.name
            new_mat = bpy.data.materials.new(name=new_mat_name)

            # Get the nodes and links
            new_mat.use_nodes = True
            nodes = new_mat.node_tree.nodes
            links = new_mat.node_tree.links

            # Get BSDF node reference
            principled_bsdf = nodes.get("Principled BSDF")
            output_node = nodes.get("Material Output")

            _x_texture_node = -1500
            _y_texture_node = 300

            """ 
            Add texture nodes START: (base color、ao、metallic、roughness、 alpha_node、
                                normal_node、displacement_node、displacement)
            """ 

            collection_of_texture_nodes = []

            # Base color
            if os.path.exists(base_image_path):
                base_color = nodes.new('ShaderNodeTexImage')
                base_color.location = (_x_texture_node, _y_texture_node)
                base_color.image =  bpy.data.images.load(base_image_path)
                links.new(base_color.outputs["Color"], principled_bsdf.inputs["Base Color"])

                collection_of_texture_nodes.append(base_color)
            
            # Ao
            if os.path.exists(ambient_occlusion_image_path):
                ao_color = nodes.new('ShaderNodeTexImage')
                ao_color.location = (_x_texture_node, _y_texture_node * 2)
                ao_color.image =  bpy.data.images.load(ambient_occlusion_image_path)
                ao_color.image.colorspace_settings.name = 'Non-Color'
                math_node = nodes.new(type='ShaderNodeMixRGB')
                math_node.blend_type = "MULTIPLY"
                math_node.location.x = _x_texture_node * 0.5
                math_node.location.y = _y_texture_node * 1.5
                math_node.inputs["Fac"].default_value = 0.333
                links.new(base_color.outputs["Color"], math_node.inputs[1])
                links.new(ao_color.outputs["Color"], math_node.inputs[2])
                links.new(math_node.outputs["Color"], principled_bsdf.inputs["Base Color"])

                collection_of_texture_nodes.append(ao_color)
            
            # Metallic
            if os.path.exists(metallic_image_path):
                metallic = nodes.new('ShaderNodeTexImage')
                metallic.location = (_x_texture_node, 0)
                metallic.image =  bpy.data.images.load(metallic_image_path)
                metallic.image.colorspace_settings.name = 'Non-Color'
                links.new(metallic.outputs["Color"], principled_bsdf.inputs["Metallic"])

                collection_of_texture_nodes.append(metallic)
            
            # Roughness
            if os.path.exists(roughness_image_path):
                roughness_texture = nodes.new('ShaderNodeTexImage')
                roughness_texture.location = (_x_texture_node, _y_texture_node * -1)
                roughness_texture.image =  bpy.data.images.load(roughness_image_path)
                roughness_texture.image.colorspace_settings.name = 'Non-Color'
                links.new(roughness_texture.outputs["Color"], principled_bsdf.inputs["Roughness"])

                collection_of_texture_nodes.append(roughness_texture)
            
            # Alpha
            if os.path.exists(alpha_image_path):
                alpha_texture = nodes.new('ShaderNodeTexImage')
                alpha_texture.location = (_x_texture_node, _y_texture_node * -2)
                alpha_texture.image =  bpy.data.images.load(alpha_image_path)
                alpha_texture.image.colorspace_settings.name = 'Non-Color'
                links.new(alpha_texture.outputs["Color"], principled_bsdf.inputs["Alpha"])

                collection_of_texture_nodes.append(alpha_texture)
            
            # Normal
            if os.path.exists(normal_image_path):
                normal_texture = nodes.new('ShaderNodeTexImage')
                normal_y_value = _y_texture_node * -3
                normal_texture.location = (_x_texture_node, normal_y_value)
                normal_texture.image =  bpy.data.images.load(normal_image_path)

                separate_rgba = nodes.new('ShaderNodeSeparateRGB')
                separate_rgba.location.x = 4.0 / 5.0 * _x_texture_node
                separate_rgba.location.y = normal_y_value
                links.new(normal_texture.outputs["Color"], separate_rgba.inputs["Image"])

                invert_node = nodes.new("ShaderNodeInvert")
                invert_node.inputs["Fac"].default_value = 1.0
                invert_node.location.x = 3.0 / 5.0 * _x_texture_node
                invert_node.location.y = normal_y_value
                links.new(separate_rgba.outputs["G"], invert_node.inputs["Color"])

                combine_rgba = nodes.new('ShaderNodeCombineRGB')
                combine_rgba.location.x = 2.0 / 5.0 * _x_texture_node
                combine_rgba.location.y = normal_y_value
                links.new(separate_rgba.outputs["R"], combine_rgba.inputs["R"])
                links.new(invert_node.outputs["Color"], combine_rgba.inputs["G"])
                links.new(separate_rgba.outputs["B"], combine_rgba.inputs["B"])

                current_output = combine_rgba.outputs["Image"]

                normal_map = nodes.new("ShaderNodeNormalMap")
                normal_map.inputs["Strength"].default_value = 1.0
                normal_map.location.x = 1.0 / 5.0 * _x_texture_node
                normal_map.location.y = normal_y_value
                links.new(current_output, normal_map.inputs["Color"])
                links.new(normal_map.outputs["Normal"], principled_bsdf.inputs["Normal"])

                collection_of_texture_nodes.append(normal_texture)

            # Displacement
            if os.path.exists(displacement_image_path):
                displacement_texture = nodes.new('ShaderNodeTexImage')
                displacement_texture.location = (_x_texture_node, _y_texture_node * -4)
                displacement_texture.image =  bpy.data.images.load(displacement_image_path)

                displacement_node = nodes.new("ShaderNodeDisplacement")
                displacement_node.inputs["Midlevel"].default_value = 0.5
                displacement_node.inputs["Scale"].default_value = 0.15
                displacement_node.location.x = _x_texture_node * 0.5
                displacement_node.location.y = _y_texture_node * -4
                links.new(displacement_texture.outputs["Color"], displacement_node.inputs["Height"])
                links.new(displacement_node.outputs["Displacement"], output_node.inputs["Displacement"])

                collection_of_texture_nodes.append(displacement_texture)

            # Connect uv
            collection_of_texture_nodes = [node for node in collection_of_texture_nodes if node is not None]
            if len(collection_of_texture_nodes) > 0:
                texture_coords = nodes.new("ShaderNodeTexCoord")
                texture_coords.location.x = _x_texture_node * 1.4
                mapping_node = nodes.new("ShaderNodeMapping")
                mapping_node.location.x = _x_texture_node * 1.2

                links.new(texture_coords.outputs["UV"], mapping_node.inputs["Vector"])
                for texture_node in collection_of_texture_nodes:
                    if texture_node is not None:
                        links.new(mapping_node.outputs["Vector"], texture_node.inputs["Vector"])

            """ 
            Add texture nodes END
            """

            # Add empty material to BG & OCC objects 
            if current_obj.data.materials:
                    current_obj.data.materials[0] = new_mat
            else:
                current_obj.data.materials.append(new_mat)


    def texture_randomize(self):
        """Randomly apply materials to objects."""
        self.__get_all_material_image_paths()
        self.__get_objects_need_assign_material()
        self.__randomly_select_materials()
        self.__create_and_assign_material()
        print('Material Randomize COMPLERED !!!')

            
if __name__ == '__main__':
    randomizer = TextureRandomizer()
    randomizer.texture_randomize()