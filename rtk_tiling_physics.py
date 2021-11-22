bl_info = {
    "name": "RTK - Tiling Physics",
    "category": "Mesh"
}

import bpy
import bmesh
import random
import math

grid_size_x = 5
grid_size_y = 5
grid_spawn_height = 1
spawn_count = 0

current_simulating_object = None
isSimulating = False

collection_name = "PhysicsObjects"

def spawnObject(object_original):
    
    global spawn_count
    global current_simulating_object
    global isSimulating
    
    grid_size = bpy.context.scene.targetGridSize
    spawn_height = bpy.context.scene.spawnHeight
    tile_size = bpy.context.scene.tileSize
    
    # Set scene frame to 0
    bpy.ops.screen.animation_cancel()
    
    # Duplicate object
    object_duplicate = object_original.copy()
    object_duplicate.data = object_original.data.copy()
    object_duplicate.animation_data_clear()
    
    # Add duplicate to collections
    bpy.data.collections[collection_name].objects.link(object_duplicate)
    
    # Set location
    object_duplicate.location.x = -(tile_size / 2) + ((spawn_count % grid_size[0]) * (tile_size / (grid_size[0] - 1)))
    object_duplicate.location.y = -(tile_size / 2) + ((math.floor(spawn_count / grid_size[0]) % grid_size[1]) * (tile_size / (grid_size[1] - 1)))
    object_duplicate.location.z = spawn_height
    
    # Set random rotation
    object_duplicate.rotation_euler.x = random.random() * 360
    object_duplicate.rotation_euler.y = random.random() * 360
    object_duplicate.rotation_euler.z = random.random() * 360
    
    # Set rigidbody type to active
    object_duplicate.rigid_body.type = 'ACTIVE'
    
    # Set curent simulating object as active
    for object in bpy.data.objects:
        object.select_set(False)
    
    object_duplicate.select_set(True)
    bpy.context.view_layer.objects.active = object_duplicate
    
    current_simulating_object = object_duplicate
    isSimulating = True
    spawn_count += 1
    
    bpy.ops.screen.animation_play()

def createTilingDuplicates(object):
    if not is_in_scene(object):
        return
    
    tile_size = bpy.context.scene.tileSize
    
    bpy.ops.object.visual_transform_apply()
    object.rigid_body.type = 'PASSIVE'
    
    maxDimensionValue = -1
    objectOutOfView = False
    
    '''
    for value in object.dimensions:
        if value > maxDimensionValue:
            maxDimensionValue = value
    
    location_values = [ object.location.x, object.location.y ]
    
    for value in location_values:
        if abs(value) > (tile_size / 2) + maxDimensionValue:
            objectOutOfView = True
            break
    '''
    
    if not objectOutOfView:
        object_duplicate_top = object.copy()
        object_duplicate_top.data = object.data.copy()
        object_duplicate_top.animation_data_clear()
        object_duplicate_top.location.y += tile_size
        
        object_duplicate_top_left = object.copy()
        object_duplicate_top_left.data = object.data.copy()
        object_duplicate_top_left.animation_data_clear()
        object_duplicate_top_left.location.x -= tile_size
        object_duplicate_top_left.location.y += tile_size
        
        object_duplicate_top_right = object.copy()
        object_duplicate_top_right.data = object.data.copy()
        object_duplicate_top_right.animation_data_clear()
        object_duplicate_top_right.location.x += tile_size
        object_duplicate_top_right.location.y += tile_size
        
        object_duplicate_bottom = object.copy()
        object_duplicate_bottom.data = object.data.copy()
        object_duplicate_bottom.animation_data_clear()
        object_duplicate_bottom.location.y -= tile_size
        
        object_duplicate_bottom_left = object.copy()
        object_duplicate_bottom_left.data = object.data.copy()
        object_duplicate_bottom_left.animation_data_clear()
        object_duplicate_bottom_left.location.x -= tile_size
        object_duplicate_bottom_left.location.y -= tile_size
        
        object_duplicate_bottom_right = object.copy()
        object_duplicate_bottom_right.data = object.data.copy()
        object_duplicate_bottom_right.animation_data_clear()
        object_duplicate_bottom_right.location.x += tile_size
        object_duplicate_bottom_right.location.y -= tile_size
        
        object_duplicate_left = object.copy()
        object_duplicate_left.data = object.data.copy()
        object_duplicate_left.animation_data_clear()
        object_duplicate_left.location.x -= tile_size
        
        object_duplicate_right = object.copy()
        object_duplicate_right.data = object.data.copy()
        object_duplicate_right.animation_data_clear()
        object_duplicate_right.location.x += tile_size
        
        bpy.data.collections[collection_name].objects.link(object_duplicate_top)
        bpy.data.collections[collection_name].objects.link(object_duplicate_top_left)
        bpy.data.collections[collection_name].objects.link(object_duplicate_top_right)
        bpy.data.collections[collection_name].objects.link(object_duplicate_bottom)
        bpy.data.collections[collection_name].objects.link(object_duplicate_bottom_left)
        bpy.data.collections[collection_name].objects.link(object_duplicate_bottom_right)
        bpy.data.collections[collection_name].objects.link(object_duplicate_left)
        bpy.data.collections[collection_name].objects.link(object_duplicate_right)

def is_in_scene(object):
    for obj in bpy.context.scene.objects:
        if obj == object:
            return True
    return False

class RTK_OT_SpawnPhysicsObjects(bpy.types.Operator):
    bl_idname = "rtk.spawn_physics_objects"
    bl_label = "Spawn Physics Objects"
    bl_description = "Spawns a new physics object randomly taken from the given collection, then starts the physics simulation"
    
    def execute(self, context):
        global current_simulating_object
        global isSimulating
        
        scene = bpy.context.scene
        
        if scene.targetCollectionName == "":
            self.report({'ERROR'}, "No collection was selected!")
            return {'FINISHED'}
        
        targetCollection = bpy.data.collections[scene.targetCollectionName]
        
        if targetCollection is None:
            return {'FINISHED'}
        
        for object in targetCollection.objects:
            if object.type != 'MESH':
                self.report({'ERROR'}, "Not all objects in " + scene.targetCollectionName + " are Mesh Objects!")
                return {'FINISHED'}
            
            if object.type == 'MESH' and object.rigid_body is None:
                self.report({'ERROR'}, "Not all objects in " + scene.targetCollectionName + " are Rigid Bodies!")
                return {'FINISHED'}
        
        if not isSimulating:
            for object in targetCollection.objects:
                object.rigid_body.type = 'PASSIVE'
        
        randomIndex = round(random.random() * (len(targetCollection.objects) - 1))
        object = targetCollection.objects[randomIndex]
        
        if object is not None and object.type == 'MESH':
            # Create collection if not yet created
            if not bpy.data.collections.get(collection_name):
                collection = bpy.data.collections.new(name=collection_name)
                bpy.context.scene.collection.children.link(collection)
            
            if isSimulating:
                createTilingDuplicates(current_simulating_object)
            
            spawnObject(object)
        
        return {'FINISHED'}

class RTK_OT_RestartSimulation(bpy.types.Operator):
    bl_idname = "rtk.restart_simulation"
    bl_label = "Restart Simulation"
    bl_description = "Respawns the last object with a new random rotation"
    
    def execute(self, context):
        global spawn_count
        global current_simulating_object
        global isSimulating
        
        if not is_in_scene(current_simulating_object):
            return {'FINISHED'}
        
        grid_size = bpy.context.scene.targetGridSize
        spawn_height = bpy.context.scene.spawnHeight
        tile_size = bpy.context.scene.tileSize
        
        # Set scene frame to 0
        bpy.ops.screen.animation_cancel()

        # Set location
        current_simulating_object.location.x = -(tile_size / 2) + (((spawn_count - 1) % grid_size[0]) * (tile_size / (grid_size[0] - 1)))
        current_simulating_object.location.y = -(tile_size / 2) + ((math.floor((spawn_count - 1) / grid_size[0]) % grid_size[1]) * (tile_size / (grid_size[1] - 1)))
        current_simulating_object.location.z = spawn_height

        # Set random rotation
        current_simulating_object.rotation_euler.x = random.random() * 360
        current_simulating_object.rotation_euler.y = random.random() * 360
        current_simulating_object.rotation_euler.z = random.random() * 360
        
        bpy.ops.screen.animation_play()
        
        return {'FINISHED'}

class RTK_OT_StopSimulation(bpy.types.Operator):
    bl_idname = "rtk.stop_simulation"
    bl_label = "Stop Simulation"
    
    def execute(self, context):
        global current_simulating_object
        global isSimulating
        
        scene = bpy.context.scene
        physicsCollection = bpy.data.collections[collection_name]
        
        createTilingDuplicates(current_simulating_object)
        bpy.ops.screen.animation_cancel()
        
        # Deselect all objects
        for object in bpy.data.objects:
            object.select_set(False)
        
        '''
        # Select objects in physics collection
        for object in physicsCollection.objects:
            object.select_set(True)
        
        # Set first object in collection as active
        bpy.context.view_layer.objects.active = physicsCollection.objects[0]
        
        # Join all objects
        bpy.ops.object.join()
        '''
        
        current_simulating_object = None
        isSimulating = False
        
        return {'FINISHED'}

class RTK_PT_Tools(bpy.types.Panel):
    bl_idname = "rtk.tools_panel"
    bl_label = "Tiling Physics Simulation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RTK"

    def draw(self, context):
        global isSimulating
        global current_simulating_object
        
        layout = self.layout
        scene = bpy.context.scene
        
        layout.prop(scene, "targetGridSize")
        
        layout.separator()
        
        layout.prop(scene, "spawnHeight")
        layout.prop(scene, "tileSize")
        
        layout.separator()
        
        layout.prop_search(scene, "targetCollectionName", bpy.data, "collections")
        
        layout.separator()
        
        layout.operator(RTK_OT_SpawnPhysicsObjects.bl_idname)
        
        if isSimulating:
            if is_in_scene(current_simulating_object):
                layout.operator(RTK_OT_RestartSimulation.bl_idname)
            layout.operator(RTK_OT_StopSimulation.bl_idname)


classes = (
    RTK_OT_SpawnPhysicsObjects,
    RTK_OT_RestartSimulation,
    RTK_OT_StopSimulation,
    RTK_PT_Tools
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.targetGridSize = bpy.props.IntVectorProperty(
        name="Grid Size", 
        size=2, 
        default=(5, 5),
        min=1,
        description="The amount of physics objects spawned over the tile size"
    )
    
    bpy.types.Scene.spawnHeight = bpy.props.FloatProperty(
        name="Spawn Height", 
        default=1,
        description="The height at which the physics objects are spawned"
    )
    
    bpy.types.Scene.tileSize = bpy.props.FloatProperty(
        name="Tile Size", 
        default=2,
        min=.01,
        description="The width/height over which to spawn and tile the physics objects"
    )
    
    bpy.types.Scene.targetCollectionName = bpy.props.StringProperty(
        name="Target Collection",
        description="The collection from which to randomly spawn physics objects"
    )

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.targetGridSize
    del bpy.types.Scene.spawnHeight
    del bpy.types.Scene.tileSize
    del bpy.types.Scene.targetCollectionName

if __name__ == "__main__":
    register()