""" YOLOLabeler

reference:
https://blender.stackexchange.com/questions/264385/object-index-blender-3-0/264394#264394
https://blender.stackexchange.com/questions/39969/any-idea-how-to-get-the-location-and-bounds-of-object-in-the-image/39983#39983
https://splunktool.com/bounding-box-from-2d-numpy-array-duplicate
https://splunktool.com/how-to-convert-2d-bounding-box-pixel-coordinates-x-y-w-h-into-relative-coordinates-yolo-format
https://github.com/DIYer22/bpycv/blob/master/bpycv/render_utils.py
https://blender.stackexchange.com/questions/84287/refresh-viewer-nodes-image-data-when-pass-index-of-id-mask-node-has-changed-in
""" 

import bpy
import numpy as np
import datetime
import os

class YOLOLabeler:
    def __init__(self,
                 output_img_path = "C:/Users/user/Documents/project/synthDet/gen_data_2/images",
                 output_label_path = "C:/Users/user/Documents/project/synthDet/gen_data_2/labels"
                 ):
                 
        self.output_img_path = output_img_path
        self.output_label_path = output_label_path
        self.__obj_name_and_id_dict = {}
        self.__obj_name_and_bbox_dict = {}
        self.__target_obj_collection = bpy.data.collections["ForegroundObjectCollection"]
        self.__minimum_obj_pixel = 30 * 30
        self.__gen_img_id = None
        self.__render_machine_id = "a"
        self.__obj_name_and_class_id_mapping = {
"book_dorkdiaries_aladdin" : 0,  
"candy_minipralines_lindt" : 1,
"candy_raffaello_confetteria" : 2,
"cereal_capn_crunch" : 3,
"cereal_cheerios_honeynut" : 4,
"cereal_corn_flakes" : 5,
"cereal_cracklinoatbran_kelloggs" : 6,
"cereal_oatmealsquares_quaker" : 7,
"cereal_puffins_barbaras" : 8,
"cereal_raisin_bran" : 9,
"cereal_rice_krispies" : 10,
"chips_gardensalsa_sunchips" : 11,
"chips_sourcream_lays" : 12,
"cleaning_freegentle_tide" : 13,
"cleaning_snuggle_henkel" : 14,
"cracker_honeymaid_nabisco" : 15,
"cracker_lightrye_wasa" : 16,
"cracker_triscuit_avocado" : 17,
"cracker_zwieback_brandt" : 18,
"craft_yarn_caron" : 19,
"drink_adrenaline_shock" : 20,
"drink_coffeebeans_kickinghorse" : 21,
"drink_greentea_itoen" : 22,
"drink_orangejuice_minutemaid" : 23,
"drink_whippingcream_lucerne" : 24,
"footware_slippers_disney" : 25,
"hygiene_poise_pads" : 26,
"lotion_essentially_nivea" : 27,
"lotion_vanilla_nivea" : 28,
"pasta_lasagne_barilla" : 29,
"pest_antbaits_terro" : 30,
"porridge_grits_quaker" : 31,
"seasoning_canesugar_candh" : 32,
"snack_breadsticks_nutella" : 33,
"snack_chips_pringles" : 34,
"snack_coffeecakes_hostess" : 35,
"snack_cookie_famousamos" : 36,
"snack_biscotti_ghiott" : 37,
"snack_cookie_petitecolier" : 38,
"snack_cookie_quadratini" : 39,
"snack_cookie_waffeletten" : 40,
"snack_cookie_walkers" : 41,
"snack_cookies_fourre" : 42,
"snack_granolabar_kashi" : 43,
"snack_granolabar_kind" : 44,
"snack_granolabar_naturevalley" : 45,
"snack_granolabar_quaker" : 46,
"snack_salame_hillshire" : 47,
"soup_chickenenchilada_progresso" : 48,
"soup_tomato_pacific" : 49,
"storage_ziploc_sandwich" : 50,
"toiletry_tissue_softly" : 51,
"toiletry_toothpaste_colgate" : 52,
"toy_cat_melissa" : 53,
"utensil_candle_decorators" : 54,
"utensil_coffee_filters" : 55,
"utensil_cottonovals_signaturecare" : 56,
"utensil_papertowels_valuecorner" : 57,
"utensil_toiletpaper_scott" : 58,
"utensil_trashbag_valuecorner" : 59,
"vitamin_centrumsilver_adults" : 60,
"vitamin_centrumsilver_men" : 61,
"vitamin_centrumsilver_woman" : 62
}

    def __create_and_switch_annotation_scene(self):
        """
        """
        scene_list = []
        for scene in bpy.data.scenes:
            scene_list.append(scene.name)

        if ("Scene_Annot" not in scene_list):
            bpy.data.scenes['Scene'].copy()
            bpy.data.scenes["Scene.001"].name = "Scene_Annot"

        bpy.context.window.scene = bpy.data.scenes["Scene_Annot"]

    def __create_gen_img_id(self):
        """ 
        """
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=8)))
        time_id = now.strftime("%Y%m%d%H%M%S").zfill(15)
        render_machine_id = self.__render_machine_id
        self.__gen_img_id = render_machine_id + time_id

        return id
    
    def  __create_id_mask_nodes(self):
        """ 
        """
        ## active compositing nodes
        bpy.data.scenes['Scene_Annot'].use_nodes = True

        ## clear all nodes
        bpy.data.scenes['Scene_Annot'].node_tree.nodes.clear()

        ## activate object index pass
        bpy.data.scenes['Scene_Annot'].view_layers["ViewLayer"].use_pass_object_index = True

        ## add new nodes
        node_RenderLayers = bpy.data.scenes['Scene_Annot'].node_tree.nodes.new("CompositorNodeRLayers")
        node_Composite = bpy.data.scenes['Scene_Annot'].node_tree.nodes.new("CompositorNodeComposite")
        node_Viewer = bpy.data.scenes['Scene_Annot'].node_tree.nodes.new("CompositorNodeViewer")
  
        node_RenderLayers.location = (-100,0)
        node_Composite.location = (250,0)
        node_Viewer.location = (600,-200)

        ## link nodes
        links = bpy.data.scenes['Scene_Annot'].node_tree.links
        links.new(node_RenderLayers.outputs["Image"], node_Composite.inputs["Image"])
        links.new(node_RenderLayers.outputs["IndexOB"], node_Viewer.inputs["Image"])

    def __add_pass_index(self):
        """ 
        """ 
        bpy.data.scenes['Scene_Annot'].view_layers["ViewLayer"].use_pass_object_index = True

        for index, obj in enumerate(self.__target_obj_collection.objects, start=1): 
            obj.pass_index = index
            self.__obj_name_and_id_dict[obj.name] = index

    def __annotation_render(self):
        """ 
        """
        ## render using Cycle
        bpy.data.scenes['Scene_Annot'].render.engine = "CYCLES"
        bpy.data.scenes['Scene_Annot'].cycles.device = "GPU"
        bpy.data.scenes['Scene_Annot'].cycles.samples = 1
        bpy.data.scenes['Scene_Annot'].cycles.use_denoising = False
        print("Start Render Annot")
        bpy.ops.render.render(scene='Scene_Annot')
        print("End Render Annot")

    def __find_obj_bbox(self):
        """ 
        """
        self.__annotation_render()
        for obj_name, id in self.__obj_name_and_id_dict.items():
            S = bpy.data.scenes['Scene_Annot']
            width  = int(S.render.resolution_x * S.render.resolution_percentage / 100)
            height = int(S.render.resolution_y * S.render.resolution_percentage / 100)
            depth  = 4

            img = np.array( bpy.data.images['Viewer Node'].pixels[:] ).reshape( [height, width, depth] )
            img = np.array( [ [ img[0] for img in row ] for row in img] )

            img = (img == id).astype(int) #https://stackoverflow.com/questions/19766757/replacing-numpy-elements-if-condition-is-met

            if img.max() == 0: # no object in view
                continue
            if (img > 0).sum() <= self.__minimum_obj_pixel: # object too small in view
                continue

            img_flip = np.flip(img,0)
            y, x = np.where(img_flip)
            top_left = [x.min(), y.min()]
            bottom_right = [x.max() + 1, y.max() + 1]

            self.__obj_name_and_bbox_dict[obj_name] = [top_left,bottom_right]

            print(f"Find {obj_name} bbox")
            print(f"Remain Obj Num: {len(self.__obj_name_and_id_dict) - id}")

    def __get_obj_class_id(self, obj_name):
        """ 
        """ 
        obj_class_id = None
        for key in self.__obj_name_and_class_id_mapping:
            if key in obj_name:
                obj_class_id = self.__obj_name_and_class_id_mapping[key]
                return obj_class_id

    def __format_coordinates(self,coordinates,obj_class_id):
        """ 
        This function takes as inputs the coordinates created by the find_bounding box() function, the current class,
        the image width and the image height and outputs the coordinates of the bounding box of the current class
        """ 
        ## If the current class is in view of the camera
        if coordinates: 
            ## Figure out the rendered image size
            render = bpy.data.scenes['Scene_Annot'].render
            fac = render.resolution_percentage * 0.01
            dw = 1./(render.resolution_x * fac)
            dh = 1./(render.resolution_y * fac)
            x = (coordinates[0][0] + coordinates[1][0])/2.0
            y = (coordinates[0][1] + coordinates[1][1])/2.0
            w = coordinates[1][0] - coordinates[0][0]
            h = coordinates[1][1] - coordinates[0][1]
            cx = x*dw
            cy = y*dh
            width = w*dw
            height = h*dh

        ## Formulate line corresponding to the bounding box of one class
            txt_coordinates = str(obj_class_id) + ' ' + str(cx) + ' ' + str(cy) + ' ' + str(width) + ' ' + str(height) + '\n'

            return txt_coordinates
            ## If the current class isn't in view of the camera, then pass
        else:
            pass

    def __get_all_coordinates(self):
        """ 
        This function takes no input and outputs the complete string with the coordinates
        of all the objects in view in the current image
        """ 
        ## Initialize the variable where we'll store the coordinates
        main_text_coordinates = ''
        ## Loop through all of the objects
        for obj_name in self.__obj_name_and_bbox_dict:
            ## Get current object's coordinates
            obj_class_id = self.__get_obj_class_id(obj_name)
            coordinates = self.__obj_name_and_bbox_dict[obj_name]
            ## Reformat coordinates to YOLOv3 format
            text_coordinates = self.__format_coordinates(coordinates, obj_class_id)
            # print(text_coordinates)

            ## If find_bounding_box() doesn't return None
            ## Update main_text_coordinates variables whith each
            ## line corresponding to each class in the frame of the current image
            if text_coordinates:
                main_text_coordinates = main_text_coordinates + text_coordinates
                                                                            
        return main_text_coordinates # Return all coordinates

    def test(self):
        """ 
        """ 
        self.__create_gen_img_id()

        ##　save png img
        img_file_path = os.path.join(self.output_img_path,  str(self.__gen_img_id)+".png")
        bpy.data.scenes["Scene"].render.filepath = img_file_path 
        print("Start Render Image")         
        #bpy.ops.render.render(write_still=True, scene='Scene')
        print("End Render Image")



        ## get objects bbox
        print("Start Find BBOX") 
        self.__create_and_switch_annotation_scene()
        self.__add_pass_index()
        self.__create_id_mask_nodes3()
        #self.__create_id_mask_nodes()
        #self.__add_pass_index()
        #print(f'obj_name_and_id_dict:{self.__obj_name_and_id_dict}')
        self. __find_obj_bbox()
        print(f'obj_name_and_bbox_dict:{self.__obj_name_and_bbox_dict}')

        # get objects labels
        text_coordinates = self.__get_all_coordinates()
        splitted_coordinates = text_coordinates.split('\n')[:-1]# Delete last '\n' in coordinates

        ## save labels
        text_file_path = os.path.join(self.output_label_path, str(self.__gen_img_id)+".txt")
        text_file = open(text_file_path, 'w+') # Open .txt file of the label
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()

        print("YOLO-coordinates:\n{}".format(splitted_coordinates))
        print("SAVE IMG AT {}".format(img_file_path))
        print("SAVE LABLE AT {}".format(text_file_path))
        print("Auto Labeling COMPLERED !!!")

        print("test ok")

    def get_and_save_yolo_label(self):
        """ 
        """ 
        self.__create_gen_img_id()
        self.__create_and_switch_annotation_scene()

        ##　save png img
        img_file_path = os.path.join(self.output_img_path,  str(self.__gen_img_id)+".png")
        bpy.data.scenes["Scene"].render.filepath = img_file_path 
        print("Start Render Image")         
        bpy.ops.render.render(write_still=True, scene='Scene')
        print("End Render Image")

        ## get objects bbox
        print("Start Find BBOX") 
        self.__create_id_mask_nodes()
        self.__add_pass_index()
        #print(f'obj_name_and_id_dict:{self.__obj_name_and_id_dict}')
        self.__find_obj_bbox()
        #print(f'obj_name_and_bbox_dict:{self.__obj_name_and_bbox_dict}')

        ## get objects labels
        text_coordinates = self.__get_all_coordinates()
        splitted_coordinates = text_coordinates.split('\n')[:-1]# Delete last '\n' in coordinates

        ## save labels
        text_file_path = os.path.join(self.output_label_path, str(self.__gen_img_id)+".txt")
        text_file = open(text_file_path, 'w+') # Open .txt file of the label
        text_file.write('\n'.join(splitted_coordinates))
        text_file.close()

        print("YOLO-coordinates:\n{}".format(splitted_coordinates))
        print("SAVE IMG AT {}".format(img_file_path))
        print("SAVE LABLE AT {}".format(text_file_path))
        print("Auto Labeling COMPLERED !!!")

if __name__ == '__main__':
    yolo_labeler = YOLOLabeler()
    yolo_labeler.get_and_save_yolo_label()       