
import bpy


class Initializer:
    """ Initializer
        Cleans up the whole scene at first and then initializes basic blender settings, the world, the renderer and
        the camera.
    """
    def __init__(self):
        """
        Attributes:
            __render_engine: Engine to use for rendering
            __render_device: Device to use for rendering
            __collection_need_create: Scene Collection need to create
            camera_location: Initial camera location
        """ 
        self.__render_engine = "CYCLES"
        self.__render_device = "GPU"
        self.__collection_need_create = ["BackgroundObjectCollection", "ForegroundObjectCollection",
                                        "OccluderCollection"]
        self.camera_location = (0, 0, 3)


    def __remove_all_data(self):
        """ Remove all data blocks except opened scripts and scene.
        """
        # Go through all attributes of bpy.data
        for collection in dir(bpy.data):
            data_structure = getattr(bpy.data, collection)
            # Check that it is a data collection
            if isinstance(data_structure, bpy.types.bpy_prop_collection) and hasattr(data_structure, "remove") \
                    and collection not in ["texts"]:
                # Go over all entities in that collection
                for block in data_structure:
                    # Skip the default scene
                    if isinstance(block, bpy.types.Scene) and block.name == "Scene":
                        continue
                    data_structure.remove(block)

    def __remove_custom_properties(self):
        """ Remove all custom properties registered at global entities like the scene.
        """
        for key in bpy.context.scene.keys():
            del bpy.context.scene[key]


    def init(self):
        """ Resets the scene to its clean state.
        This method removes all objects, camera poses and cleans up the world background.
        """
        # Switch to right context
        if bpy.context.object is not None and bpy.context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT')

        # Clean up data in blender file
        self.__remove_all_data()
        self.__remove_custom_properties()

        # Create new world
        new_world = bpy.data.worlds.new("World")
        bpy.context.scene.world = new_world
        new_world["category_id"] = 0

        # Create the camera
        cam = bpy.data.cameras.new("Camera")
        cam_ob = bpy.data.objects.new("Camera", cam)
        bpy.context.scene.collection.objects.link(cam_ob)
        bpy.context.scene.camera = cam_ob
        cam_ob.location = self.camera_location

        # Create new synthdet collections
        for collection in self.__collection_need_create:
            bpy.context.scene.collection.children.link(bpy.data.collections.new(collection))

        ## Set rendering setting
        bpy.context.scene.render.engine = self.__render_engine
        bpy.context.scene.cycles.device = self.__render_device

        print("INITIALIZE COMPLERED !!!")


if __name__ == '__main__':
    initializer = Initializer()
    initializer.init()