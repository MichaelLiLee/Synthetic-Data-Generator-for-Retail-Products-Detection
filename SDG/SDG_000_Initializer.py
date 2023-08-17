import bpy


class Initializer:
    """
    A class to cleans up the whole scene at first and then initializes basic blender settings, the world,
    the renderer, the camera and create scene collections.

    Attributes
    ----------
    __render_engine (str): Engine to use for rendering.
    __render_device (str): Device to use for rendering.
    __collection_need_create (list): Scene Collection need to create.
    __camera_location (tuple): Initial camera location.

    Methods
    -------
    __remove_all_data(): Remove all data blocks except opened scripts and scene.
    init(): Initialize the blender scene to its initial state.

    References
    ----------
    https://github.com/DLR-RM/BlenderProc/blob/ea934e1b5df747dfcb5faf177092e156e5ca3356/blenderproc/python/utility/Initializer.py
    
    """

    def __init__(self):
        self.__render_engine = "CYCLES"
        self.__render_device = "GPU"
        self.__collection_need_create = ["BackgroundObjectCollection", "ForegroundObjectCollection",
                                        "OccluderCollection"]
        self.__camera_location = (0, 0, 3)


    def __remove_all_data(self):
        """Remove all data blocks except opened scripts and scene."""
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
        """Remove all custom properties registered at global entities like the scene."""
        for key in bpy.context.scene.keys():
            del bpy.context.scene[key]


    def init(self):
        """Initialize the blender scene to its initial state."""
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
        cam_ob.location = self.__camera_location

        # Create new synthdet collections
        for collection in self.__collection_need_create:
            bpy.context.scene.collection.children.link(bpy.data.collections.new(collection))

        # Set rendering setting
        bpy.context.scene.render.engine = self.__render_engine
        bpy.context.scene.cycles.device = self.__render_device

        print("INITIALIZE COMPLERED !!!")


if __name__ == '__main__':
    initializer = Initializer()
    initializer.init()